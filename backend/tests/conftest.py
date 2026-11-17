"""Configuracao compartilhada para testes de integracao."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def sem_chave_de_ia(monkeypatch):
    """Os testes nunca usam a chave real do Gemini.

    O container do backend pode ter GEMINI_API_KEY definida no .env; sem este
    isolamento, os testes fariam chamadas reais a API externa e o resultado
    dependeria do ambiente. Testes que precisam de uma chave definem uma falsa.
    """
    monkeypatch.setattr("app.services.assistente_ia.GEMINI_API_KEY", "", raising=False)


@pytest.fixture()
def client():
    return TestClient(app)
