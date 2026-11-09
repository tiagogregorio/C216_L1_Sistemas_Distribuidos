"""Acesso ao banco para os recursos simulado e resposta."""

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.questao import Questao
from app.models.resposta import Resposta
from app.models.simulado import Simulado


class SimuladoRepository:
    """Unico ponto que conversa com o banco sobre simulados."""

    def __init__(self, db: Session):
        self.db = db

    def criar(
        self,
        nome: str,
        total_questoes: int,
        questao_ids: list[int],
        ciclo: int = 1,
    ) -> Simulado:
        """Cria o simulado e ja associa as questoes sorteadas (respostas em
        branco), para que o simulado possa ser retomado mesmo antes de
        qualquer resposta ser enviada."""
        simulado = Simulado(nome=nome, total_questoes=total_questoes, ciclo=ciclo)
        self.db.add(simulado)
        self.db.flush()

        for questao_id in questao_ids:
            self.db.add(Resposta(simulado_id=simulado.id, questao_id=questao_id))

        self.db.commit()
        self.db.refresh(simulado)
        return simulado

    def buscar_por_id(self, simulado_id: int) -> Simulado | None:
        return self.db.get(Simulado, simulado_id)

    def listar(self) -> list[Simulado]:
        consulta = select(Simulado).order_by(Simulado.criado_em.desc())
        return list(self.db.scalars(consulta))

    def adicionar_respostas(
        self, simulado: Simulado, respostas: list[dict]
    ) -> list[Resposta]:
        """Preenche as respostas e calcula nota do simulado.

        As linhas de Resposta ja existem (criadas em branco junto com o
        simulado), entao aqui apenas atualizamos a resposta escolhida; se
        por algum motivo a linha nao existir, criamos uma nova.
        """
        objetos = []
        for r in respostas:
            existente = self.db.scalar(
                select(Resposta).where(
                    Resposta.simulado_id == simulado.id,
                    Resposta.questao_id == r["questao_id"],
                )
            )
            if existente is not None:
                existente.alternativa_escolhida = r["alternativa_escolhida"]
                existente.correta = r["correta"]
                existente.tempo_resposta = r.get("tempo_resposta")
                objetos.append(existente)
            else:
                resp = Resposta(
                    simulado_id=simulado.id,
                    questao_id=r["questao_id"],
                    alternativa_escolhida=r["alternativa_escolhida"],
                    correta=r["correta"],
                    tempo_resposta=r.get("tempo_resposta"),
                )
                self.db.add(resp)
                objetos.append(resp)

        acertos = sum(1 for r in respostas if r["correta"])
        simulado.finalizado = True
        simulado.acertos = acertos
        simulado.nota = round((acertos / simulado.total_questoes) * 100, 2)

        self.db.commit()
        for obj in objetos:
            self.db.refresh(obj)
        self.db.refresh(simulado)
        return objetos

    def remover(self, simulado: Simulado) -> None:
        self.db.delete(simulado)
        self.db.commit()

    def contar(self, finalizado: bool | None = None) -> int:
        consulta = select(func.count()).select_from(Simulado)
        if finalizado is not None:
            consulta = consulta.where(Simulado.finalizado == finalizado)
        return self.db.scalar(consulta) or 0

    def media_nota(self) -> float | None:
        """Retorna a media das notas dos simulados finalizados."""
        consulta = select(func.avg(Simulado.nota)).where(Simulado.finalizado.is_(True))
        resultado = self.db.scalar(consulta)
        return round(resultado, 2) if resultado is not None else None

    def total_acertos_e_respostas(self) -> tuple[int, int]:
        """Retorna total de acertos e total de respostas."""
        consulta_total = select(func.count()).select_from(Resposta)
        consulta_acertos = (
            select(func.count()).select_from(Resposta).where(Resposta.correta.is_(True))
        )
        total = self.db.scalar(consulta_total) or 0
        acertos = self.db.scalar(consulta_acertos) or 0
        return acertos, total

    def desempenho_por_ano(self) -> list[dict]:
        """Agrupa acertos e total de respostas por ano da questao."""
        soma_acertos = func.sum(case((Resposta.correta.is_(True), 1), else_=0))

        consulta = (
            select(
                Questao.ano,
                func.count(Resposta.id).label("total"),
                soma_acertos.label("acertos"),
            )
            .join(Questao, Resposta.questao_id == Questao.id)
            .where(Resposta.correta.is_not(None))
            .group_by(Questao.ano)
            .order_by(Questao.ano)
        )

        resultados = self.db.execute(consulta).all()
        return [
            {
                "ano": r.ano,
                "total": r.total,
                "acertos": int(r.acertos or 0),
                "taxa": round((int(r.acertos or 0) / r.total) * 100, 2)
                if r.total > 0
                else 0,
            }
            for r in resultados
        ]

    def desempenho_por_assunto(self) -> list[dict]:
        """Agrupa acertos, total e tempo medio de resposta por assunto."""
        soma_acertos = func.sum(case((Resposta.correta.is_(True), 1), else_=0))

        consulta = (
            select(
                Questao.assunto,
                func.count(Resposta.id).label("total"),
                soma_acertos.label("acertos"),
                func.avg(Resposta.tempo_resposta).label("tempo_medio"),
            )
            .join(Questao, Resposta.questao_id == Questao.id)
            .where(Resposta.correta.is_not(None))
            .where(Questao.assunto.is_not(None))
            .group_by(Questao.assunto)
            .order_by(Questao.assunto)
        )

        resultados = self.db.execute(consulta).all()
        return [
            {
                "assunto": r.assunto,
                "total": r.total,
                "acertos": int(r.acertos or 0),
                "taxa": round((int(r.acertos or 0) / r.total) * 100, 2)
                if r.total > 0
                else 0,
                "tempo_medio": round(r.tempo_medio, 1)
                if r.tempo_medio is not None
                else None,
            }
            for r in resultados
        ]

    def questoes_erradas(self, limite: int = 50) -> list[dict]:
        """Lista as respostas erradas mais recentes, com os dados da
        questao, para o relatorio de revisao."""
        consulta = (
            select(Resposta, Questao)
            .join(Questao, Resposta.questao_id == Questao.id)
            .where(Resposta.correta.is_(False))
            .order_by(Resposta.id.desc())
            .limit(limite)
        )
        resultados = self.db.execute(consulta).all()
        return [
            {
                "questao_id": questao.id,
                "ano": questao.ano,
                "numero": questao.numero,
                "assunto": questao.assunto,
                "enunciado": questao.enunciado,
                "alternativa_escolhida": resposta.alternativa_escolhida,
                "resposta_correta": questao.resposta,
            }
            for resposta, questao in resultados
        ]

    def desempenho_por_tipo(self) -> list[dict]:
        """Agrupa acertos e total de respostas por tipo (FG/CE)."""
        soma_acertos = func.sum(case((Resposta.correta.is_(True), 1), else_=0))

        consulta = (
            select(
                Questao.tipo,
                func.count(Resposta.id).label("total"),
                soma_acertos.label("acertos"),
            )
            .join(Questao, Resposta.questao_id == Questao.id)
            .where(Resposta.correta.is_not(None))
            .group_by(Questao.tipo)
            .order_by(Questao.tipo)
        )

        resultados = self.db.execute(consulta).all()
        return [
            {
                "tipo": r.tipo,
                "total": r.total,
                "acertos": int(r.acertos or 0),
                "taxa": round((int(r.acertos or 0) / r.total) * 100, 2)
                if r.total > 0
                else 0,
            }
            for r in resultados
        ]
