"""Acesso ao banco para o recurso questoes."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ciclo import CicloCobertura
from app.models.questao import Questao
from app.models.resposta import Resposta
from app.models.simulado import Simulado


class QuestaoRepository:
    """Unico ponto que conversa com o banco sobre questoes."""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> Questao:
        questao = Questao(**dados)
        self.db.add(questao)
        self.db.commit()
        self.db.refresh(questao)
        return questao

    def buscar_por_id(self, questao_id: int) -> Questao | None:
        return self.db.get(Questao, questao_id)

    def listar(
        self,
        ano: int | None = None,
        tipo: str | None = None,
        assunto: str | None = None,
        dificuldade: str | None = None,
    ) -> list[Questao]:
        consulta = select(Questao).order_by(Questao.ano, Questao.numero)
        if ano is not None:
            consulta = consulta.where(Questao.ano == ano)
        if tipo is not None:
            consulta = consulta.where(Questao.tipo == tipo)
        if assunto is not None:
            consulta = consulta.where(Questao.assunto.ilike(f"%{assunto}%"))
        if dificuldade is not None:
            consulta = consulta.where(Questao.dificuldade == dificuldade)
        return list(self.db.scalars(consulta))

    def listar_aleatorio(
        self,
        quantidade: int,
        ano: int | None = None,
        tipo: str | None = None,
        dificuldade: str | None = None,
        excluir_ids: list[int] | None = None,
    ) -> list[Questao]:
        """Retorna questoes aleatorias com filtros opcionais.

        `excluir_ids` e usado pelo modo "sem repetir": passa a lista de
        questoes ja respondidas para que nao sejam sorteadas de novo.
        """
        consulta = select(Questao)
        if ano is not None:
            consulta = consulta.where(Questao.ano == ano)
        if tipo is not None:
            consulta = consulta.where(Questao.tipo == tipo)
        if dificuldade is not None:
            consulta = consulta.where(Questao.dificuldade == dificuldade)
        if excluir_ids:
            consulta = consulta.where(Questao.id.not_in(excluir_ids))
        consulta = consulta.order_by(func.random()).limit(quantidade)
        return list(self.db.scalars(consulta))

    def contar(
        self,
        ano: int | None = None,
        tipo: str | None = None,
    ) -> int:
        consulta = select(func.count()).select_from(Questao)
        if ano is not None:
            consulta = consulta.where(Questao.ano == ano)
        if tipo is not None:
            consulta = consulta.where(Questao.tipo == tipo)
        return self.db.scalar(consulta) or 0

    def atualizar(self, questao: Questao, alteracoes: dict) -> Questao:
        for campo, valor in alteracoes.items():
            setattr(questao, campo, valor)
        self.db.commit()
        self.db.refresh(questao)
        return questao

    def remover(self, questao: Questao) -> None:
        self.db.delete(questao)
        self.db.commit()

    def anos_disponiveis(self) -> list[int]:
        """Retorna os anos distintos presentes no banco."""
        consulta = select(Questao.ano).distinct().order_by(Questao.ano)
        return list(self.db.scalars(consulta))

    def obter_ciclo_atual(self) -> int:
        """Retorna o ciclo de cobertura atual, criando a linha de
        controle (id=1) se ainda nao existir."""
        linha = self.db.get(CicloCobertura, 1)
        if linha is None:
            linha = CicloCobertura(id=1, valor=1)
            self.db.add(linha)
            self.db.commit()
            self.db.refresh(linha)
        return linha.valor

    def reiniciar_ciclo(self) -> int:
        """Inicia um novo ciclo de cobertura (incrementa o valor atual).

        Simulados e respostas anteriores nao sao apagados — apenas param
        de contar para a barra de cobertura do modo "sem repetir", que
        volta a zero para o novo ciclo.
        """
        linha = self.db.get(CicloCobertura, 1)
        if linha is None:
            linha = CicloCobertura(id=1, valor=1)
            self.db.add(linha)
        else:
            linha.valor += 1
        self.db.commit()
        self.db.refresh(linha)
        return linha.valor

    def ids_respondidas_no_ciclo(self, ciclo: int) -> list[int]:
        """IDs de questoes ja respondidas dentro do ciclo de cobertura
        informado. Usado pelo modo "sem repetir" para nao sortear a mesma
        questao duas vezes dentro do mesmo ciclo."""
        consulta = (
            select(Resposta.questao_id)
            .join(Simulado, Resposta.simulado_id == Simulado.id)
            .where(Resposta.alternativa_escolhida.is_not(None))
            .where(Simulado.ciclo == ciclo)
            .distinct()
        )
        return list(self.db.scalars(consulta))

    def cobertura(self) -> dict:
        """Quantas questoes do banco ja foram respondidas no ciclo atual,
        para a barra de progresso do modo "sem repetir"."""
        ciclo_atual = self.obter_ciclo_atual()
        total = self.contar()
        respondidas = len(self.ids_respondidas_no_ciclo(ciclo_atual))
        percentual = round((respondidas / total) * 100, 2) if total > 0 else 0.0
        return {
            "ciclo": ciclo_atual,
            "total": total,
            "respondidas": respondidas,
            "restantes": total - respondidas,
            "percentual": percentual,
        }

    def contagem_por_alternativa(self, questao_id: int) -> dict[str, int]:
        """Conta quantas vezes cada alternativa foi escolhida nesta questao."""
        consulta = (
            select(Resposta.alternativa_escolhida, func.count().label("total"))
            .where(Resposta.questao_id == questao_id)
            .where(Resposta.alternativa_escolhida.is_not(None))
            .group_by(Resposta.alternativa_escolhida)
        )
        resultados = self.db.execute(consulta).all()
        contagem = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
        for letra, total in resultados:
            if letra in contagem:
                contagem[letra] = total
        return contagem
