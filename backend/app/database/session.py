"""Engine, fabrica de sessoes e dependencia de sessao do banco."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL

# O engine e criado uma unica vez e mantem o pool de conexoes.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Iterator[Session]:
    """Dependencia do FastAPI: uma sessao por requisicao, sempre fechada."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
