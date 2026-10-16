"""Acesso ao banco para o recurso tarefas."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.tarefa import Tarefa


class TarefaRepository:
    """Unico ponto da aplicacao que conversa com o banco sobre tarefas."""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, titulo: str, prioridade: str, status: str) -> Tarefa:
        tarefa = Tarefa(titulo=titulo, prioridade=prioridade, status=status)
        self.db.add(tarefa)
        self.db.commit()
        self.db.refresh(tarefa)
        return tarefa

    def buscar_por_id(self, tarefa_id: int) -> Tarefa | None:
        return self.db.get(Tarefa, tarefa_id)

    def listar(self, status: str | None = None) -> list[Tarefa]:
        consulta = select(Tarefa).order_by(Tarefa.id)
        if status is not None:
            consulta = consulta.where(Tarefa.status == status)
        return list(self.db.scalars(consulta))

    def contar(self, status: str | None = None) -> int:
        consulta = select(func.count()).select_from(Tarefa)
        if status is not None:
            consulta = consulta.where(Tarefa.status == status)
        return self.db.scalar(consulta) or 0

    def atualizar(self, tarefa: Tarefa, alteracoes: dict) -> Tarefa:
        for campo, valor in alteracoes.items():
            setattr(tarefa, campo, valor)
        self.db.commit()
        self.db.refresh(tarefa)
        return tarefa

    def remover(self, tarefa: Tarefa) -> None:
        self.db.delete(tarefa)
        self.db.commit()
