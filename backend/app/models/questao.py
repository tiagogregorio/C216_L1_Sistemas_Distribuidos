"""Modelo ORM da tabela de questoes do ENADE."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Questao(Base):
    """Representa uma questao objetiva do ENADE armazenada no banco."""

    __tablename__ = "questoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    ano: Mapped[int] = mapped_column()
    numero: Mapped[int] = mapped_column()
    tipo: Mapped[str] = mapped_column(String(2))
    enunciado: Mapped[str] = mapped_column(Text)
    alternativa_a: Mapped[str] = mapped_column(Text)
    alternativa_b: Mapped[str] = mapped_column(Text)
    alternativa_c: Mapped[str] = mapped_column(Text)
    alternativa_d: Mapped[str] = mapped_column(Text)
    alternativa_e: Mapped[str] = mapped_column(Text)
    resposta: Mapped[str] = mapped_column(String(1))
    assunto: Mapped[str | None] = mapped_column(String(100), nullable=True)
    dificuldade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    imagem: Mapped[str | None] = mapped_column(Text, nullable=True)
