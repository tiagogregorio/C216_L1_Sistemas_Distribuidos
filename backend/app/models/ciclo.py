"""Modelo que rastreia o ciclo atual de cobertura das questoes."""

from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class CicloCobertura(Base):
    """Linha unica (id=1) guardando em qual "ciclo" de cobertura estamos.

    Cada vez que o usuario reinicia a cobertura (para refazer 100% das
    questoes do zero, no modo "sem repetir"), este valor e incrementado.
    Simulados guardam o ciclo em que foram criados; apenas respostas do
    ciclo atual contam para a barra de cobertura. O historico e o
    dashboard continuam mostrando todos os ciclos, nada e apagado.
    """

    __tablename__ = "ciclo_cobertura"

    id: Mapped[int] = mapped_column(primary_key=True)
    valor: Mapped[int] = mapped_column(default=1, server_default="1")
