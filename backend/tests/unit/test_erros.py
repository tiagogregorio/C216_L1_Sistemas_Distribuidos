"""Erros 500 precisam chegar ao navegador com CORS, senao viram "NetworkError"."""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.core.erros import registrar_tratamento_de_erros

ORIGEM = "http://localhost:5173"


def criar_app(com_tratamento: bool) -> FastAPI:
    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=[ORIGEM], allow_methods=["*"])
    if com_tratamento:
        registrar_tratamento_de_erros(app, [ORIGEM])

    @app.get("/boom")
    def boom():
        raise RuntimeError("coluna x nao existe\nlinha de detalhe extra")

    return app


def chamar(app: FastAPI, origem: str):
    cliente = TestClient(app, raise_server_exceptions=False)
    return cliente.get("/boom", headers={"Origin": origem})


def test_sem_tratamento_o_500_perde_o_cors():
    """Documenta o problema: o navegador nao consegue ler essa resposta."""
    resposta = chamar(criar_app(com_tratamento=False), ORIGEM)
    assert resposta.status_code == 500
    assert "access-control-allow-origin" not in resposta.headers


def test_com_tratamento_o_500_mantem_cors_e_diz_a_causa():
    resposta = chamar(criar_app(com_tratamento=True), ORIGEM)
    assert resposta.status_code == 500
    assert resposta.headers["access-control-allow-origin"] == ORIGEM
    detalhe = resposta.json()["detail"]
    assert "RuntimeError" in detalhe
    assert "coluna x nao existe" in detalhe
    assert "linha de detalhe extra" not in detalhe  # so a primeira linha


def test_origem_nao_permitida_nao_recebe_cors():
    resposta = chamar(criar_app(com_tratamento=True), "http://site-estranho.com")
    assert resposta.status_code == 500
    assert "access-control-allow-origin" not in resposta.headers


def test_o_app_real_usa_o_tratamento():
    from app.main import app

    assert Exception in app.exception_handlers


@pytest.mark.parametrize("numero", [1])
def test_marcacao_de_questoes_vazias_e_misturadas(monkeypatch, numero):
    """Em duas colunas, a questao sem cabecalho some e a anterior se contamina."""
    from app.services import importacao_pdf

    texto = (
        "QUESTÃO 1 A\nQUESTÃO 2 B\nQUESTÃO 3 C\n"
        "QUESTÃO 01\nEnunciado completo da primeira questao\n"
        "A um\nB dois\nC tres\nD quatro\nE cinco\n"
        "QUESTÃO 03\nEnunciado completo da terceira questao\n"
        "A um\nB dois\nC tres\nD quatro\nE cinco\n"
    )
    monkeypatch.setattr(importacao_pdf, "extrair_texto", lambda _caminho: texto)
    monkeypatch.setattr(importacao_pdf, "rasterizar_paginas", lambda *_a, **_k: 0)
    monkeypatch.setattr(importacao_pdf, "_gerar_miniaturas", lambda _p: [])

    resultado = importacao_pdf.processar_pdf(b"%PDF-falso", ano=2023, inicio_ce=1)
    por_numero = {q["numero"]: q for q in resultado["questoes"]}

    assert por_numero[1]["mistura_possivel"] is True  # a 2 nao foi achada
    assert por_numero[1]["sem_texto"] is False
    assert por_numero[2]["sem_texto"] is True
    assert por_numero[2]["enunciado"] == ""
    assert por_numero[3]["sem_texto"] is False
    assert por_numero[3]["mistura_possivel"] is False
