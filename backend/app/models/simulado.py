"""Modelo ORM da tabela de simulados."""

from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Simulado(Base):
    """Representa um simulado (prova) gerado pelo usuario."""

    __tablename__ = "simulados"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    finalizado: Mapped[bool] = mapped_column(default=False)
    total_questoes: Mapped[int] = mapped_column(default=0)
    acertos: Mapped[int | None] = mapped_column(nullable=True)
    nota: Mapped[float | None] = mapped_column(nullable=True)
    ciclo: Mapped[int] = mapped_column(default=1, server_default="1")
    """Ciclo de cobertura em que este simulado foi criado (ver CicloCobertura)."""

    respostas: Mapped[list["Resposta"]] = relationship(
        back_populates="simulado",
        cascade="all, delete-orphan",
    )


from app.models.resposta import Resposta  # noqa: E402
