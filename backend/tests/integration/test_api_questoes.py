"""Testes de integracao dos endpoints de questoes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

QUESTAO_VALIDA = {
    "ano": 2019,
    "numero": 9,
    "tipo": "CE",
    "enunciado": "Questao de teste para validacao do endpoint da API REST.",
    "alternativa_a": "Alternativa A do teste",
    "alternativa_b": "Alternativa B do teste",
    "alternativa_c": "Alternativa C do teste",
    "alternativa_d": "Alternativa D do teste",
    "alternativa_e": "Alternativa E do teste",
    "resposta": "C",
    "assunto": "Testes",
    "dificuldade": "facil",
}


class TestCriarQuestao:
    def test_criar_questao_valida(self):
        response = client.post("/questoes/", json=QUESTAO_VALIDA)
        assert response.status_code == 201
        data = response.json()
        assert data["ano"] == 2019
        assert data["resposta"] == "C"
        assert "id" in data

    def test_criar_questao_tipo_invalido(self):
        dados = {**QUESTAO_VALIDA, "tipo": "XX"}
        response = client.post("/questoes/", json=dados)
        assert response.status_code == 422


class TestListarQuestoes:
    def test_listar_vazio(self):
        response = client.get("/questoes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_com_filtro_ano(self):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/?ano=2019")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_listar_filtro_ano_sem_resultado(self):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/?ano=2014")
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestBuscarQuestao:
    def test_buscar_existente(self):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.get(f"/questoes/{criada['id']}")
        assert response.status_code == 200
        assert response.json()["enunciado"] == QUESTAO_VALIDA["enunciado"]

    def test_buscar_inexistente(self):
        response = client.get("/questoes/999")
        assert response.status_code == 404


class TestAtualizarQuestao:
    def test_patch_parcial(self):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.patch(
            f"/questoes/{criada['id']}", json={"dificuldade": "dificil"}
        )
        assert response.status_code == 200
        assert response.json()["dificuldade"] == "dificil"


class TestRemoverQuestao:
    def test_remover_existente(self):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.delete(f"/questoes/{criada['id']}")
        assert response.status_code == 204

    def test_remover_inexistente(self):
        response = client.delete("/questoes/999")
        assert response.status_code == 404


class TestResumoQuestoes:
    def test_resumo_com_dados(self):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/resumo")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["componente_especifico"] == 1
