"""Acesso ao banco para o recurso questoes."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.questao import Questao


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
    ) -> list[Questao]:
        """Retorna questoes aleatorias com filtros opcionais."""
        consulta = select(Questao)
        if ano is not None:
            consulta = consulta.where(Questao.ano == ano)
        if tipo is not None:
            consulta = consulta.where(Questao.tipo == tipo)
        if dificuldade is not None:
            consulta = consulta.where(Questao.dificuldade == dificuldade)
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
