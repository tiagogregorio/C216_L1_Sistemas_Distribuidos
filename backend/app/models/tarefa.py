"""Modelo ORM da tabela de tarefas."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Tarefa(Base):
    """Representa como uma tarefa e armazenada no banco."""

    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(80))
    prioridade: Mapped[str] = mapped_column(String(10), default="media")
    status: Mapped[str] = mapped_column(String(10), default="pendente")
