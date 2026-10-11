import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import tarefas as servico


@pytest.fixture(autouse=True)
def armazenamento_limpo():
    """Zera o armazenamento em memoria antes e depois de cada teste."""
    servico.resetar()
    yield
    servico.resetar()


@pytest.fixture
def client() -> TestClient:
    """Cliente HTTP de teste usado nos testes de integracao."""
    return TestClient(app)


@pytest.fixture
def tarefas_exemplo() -> list[dict]:
    """Massa de dados mocada, usada pelos testes unitarios."""
    return [
        {"id": 1, "titulo": "Estudar pytest", "status": "concluida"},
        {"id": 2, "titulo": "Configurar CI", "status": "pendente"},
        {"id": 3, "titulo": "Abrir PR", "status": "concluida"},
        {"id": 4, "titulo": "Revisar codigo", "status": "pendente"},
    ]


@pytest.fixture
def tarefa_criada(client: TestClient) -> dict:
    """Cria uma tarefa via API e devolve o corpo da resposta."""
    resposta = client.post(
        "/tarefas",
        json={"titulo": "Estudar FastAPI", "prioridade": "alta"},
    )
    return resposta.json()
