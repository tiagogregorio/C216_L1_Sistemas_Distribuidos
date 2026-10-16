"""Base declarativa compartilhada por todos os models do SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base da qual todos os models herdam."""
