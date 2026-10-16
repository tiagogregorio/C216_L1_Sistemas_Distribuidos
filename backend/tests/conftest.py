"""Fixtures compartilhadas por todos os testes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app


@pytest.fixture
def client():
    """Client com banco SQLite em memoria, isolado por teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def tarefa_criada(client: TestClient) -> dict:
    """Cria uma tarefa via API e devolve o corpo da resposta."""
    resposta = client.post(
        "/tarefas",
        json={"titulo": "Estudar FastAPI", "prioridade": "alta"},
    )
    return resposta.json()
