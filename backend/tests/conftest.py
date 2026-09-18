import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    """Cliente HTTP de teste usado nos testes de integracao."""
    return TestClient(app)


@pytest.fixture
def tarefas_exemplo() -> list[dict]:
    """Massa de dados mocada, reutilizada pelos testes unitarios."""
    return [
        {"id": 1, "titulo": "Estudar pytest", "status": "concluida"},
        {"id": 2, "titulo": "Configurar CI", "status": "pendente"},
        {"id": 3, "titulo": "Abrir PR", "status": "concluida"},
        {"id": 4, "titulo": "Revisar codigo", "status": "pendente"},
    ]
