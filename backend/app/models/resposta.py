"""Modelo ORM da tabela de respostas de cada simulado."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Resposta(Base):
    """Representa a resposta de uma questao dentro de um simulado."""

    __tablename__ = "respostas"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulado_id: Mapped[int] = mapped_column(ForeignKey("simulados.id"))
    questao_id: Mapped[int] = mapped_column(ForeignKey("questoes.id"))
    alternativa_escolhida: Mapped[str | None] = mapped_column(
        String(1), nullable=True
    )
    correta: Mapped[bool | None] = mapped_column(nullable=True)
    tempo_resposta: Mapped[float | None] = mapped_column(nullable=True)

    simulado: Mapped["Simulado"] = relationship(back_populates="respostas")

    questao: Mapped["Questao"] = relationship()


from app.models.questao import Questao  # noqa: E402, F811
from app.models.simulado import Simulado  # noqa: E402, F811
