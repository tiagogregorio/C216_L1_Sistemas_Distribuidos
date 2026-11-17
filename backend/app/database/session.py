"""Gerenciamento de sessao e engine do banco de dados."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessao do banco para cada requisicao."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
