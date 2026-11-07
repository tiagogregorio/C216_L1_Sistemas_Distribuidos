"""Testes de integracao dos endpoints de simulados."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sim.db"

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

QUESTAO = {
    "ano": 2019,
    "numero": 1,
    "tipo": "CE",
    "enunciado": "Questao de teste para simulado completo da plataforma.",
    "alternativa_a": "Opcao A",
    "alternativa_b": "Opcao B",
    "alternativa_c": "Opcao C",
    "alternativa_d": "Opcao D",
    "alternativa_e": "Opcao E",
    "resposta": "A",
    "dificuldade": "facil",
}


def criar_questoes(n=5):
    ids = []
    for i in range(n):
        q = {**QUESTAO, "numero": i + 1}
        resp = client.post("/questoes/", json=q)
        ids.append(resp.json()["id"])
    return ids


class TestCriarSimulado:
    def test_criar_simulado_com_questoes(self):
        criar_questoes(5)
        response = client.post(
            "/simulados/",
            json={"nome": "Teste Simulado", "quantidade": 3},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["simulado"]["nome"] == "Teste Simulado"
        assert len(data["questao_ids"]) == 3

    def test_criar_simulado_questoes_insuficientes(self):
        criar_questoes(2)
        response = client.post(
            "/simulados/",
            json={"nome": "Teste Sem Questoes", "quantidade": 10},
        )
        assert response.status_code == 422


class TestSubmeterRespostas:
    def test_submeter_e_corrigir(self):
        criar_questoes(3)
        criado = client.post(
            "/simulados/",
            json={"nome": "Simulado Correcao", "quantidade": 3},
        ).json()

        simulado_id = criado["simulado"]["id"]
        questao_ids = criado["questao_ids"]

        respostas = [
            {"questao_id": questao_ids[0], "alternativa_escolhida": "A"},
            {"questao_id": questao_ids[1], "alternativa_escolhida": "B"},
            {"questao_id": questao_ids[2], "alternativa_escolhida": "A"},
        ]

        response = client.post(
            f"/simulados/{simulado_id}/submeter",
            json={"respostas": respostas},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["finalizado"] is True
        assert data["nota"] is not None

    def test_submeter_simulado_ja_finalizado(self):
        criar_questoes(2)
        criado = client.post(
            "/simulados/",
            json={"nome": "Ja Finalizado", "quantidade": 2},
        ).json()

        simulado_id = criado["simulado"]["id"]
        questao_ids = criado["questao_ids"]

        respostas = [
            {"questao_id": qid, "alternativa_escolhida": "A"}
            for qid in questao_ids
        ]
        client.post(
            f"/simulados/{simulado_id}/submeter",
            json={"respostas": respostas},
        )

        response = client.post(
            f"/simulados/{simulado_id}/submeter",
            json={"respostas": respostas},
        )
        assert response.status_code == 409


class TestDashboard:
    def test_dashboard_vazio(self):
        response = client.get("/simulados/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_simulados"] == 0

    def test_dashboard_com_dados(self):
        criar_questoes(3)
        criado = client.post(
            "/simulados/",
            json={"nome": "Dashboard Test", "quantidade": 3},
        ).json()

        respostas = [
            {"questao_id": qid, "alternativa_escolhida": "A"}
            for qid in criado["questao_ids"]
        ]
        client.post(
            f"/simulados/{criado['simulado']['id']}/submeter",
            json={"respostas": respostas},
        )

        response = client.get("/simulados/dashboard")
        data = response.json()
        assert data["simulados_finalizados"] == 1
        assert data["media_nota"] is not None


class TestRemoverSimulado:
    def test_remover_existente(self):
        criar_questoes(2)
        criado = client.post(
            "/simulados/",
            json={"nome": "Para Remover", "quantidade": 2},
        ).json()
        response = client.delete(
            f"/simulados/{criado['simulado']['id']}"
        )
        assert response.status_code == 204
