"""Testes unitarios do assistente de IA (integracao com o Gemini)."""

import asyncio

import pytest

from app.models.questao import Questao
from app.services.assistente_ia import (
    AssistenteIAIndisponivelError,
    explicar_questao,
    montar_prompt,
)


def questao_exemplo() -> Questao:
    return Questao(
        id=1,
        ano=2019,
        numero=1,
        tipo="CE",
        enunciado="Qual estrutura de dados usa LIFO?",
        alternativa_a="Fila",
        alternativa_b="Pilha",
        alternativa_c="Lista",
        alternativa_d="Arvore",
        alternativa_e="Grafo",
        resposta="B",
    )


class TestMontarPrompt:
    def test_inclui_enunciado_e_alternativas(self):
        prompt = montar_prompt(questao_exemplo())
        assert "Qual estrutura de dados usa LIFO?" in prompt
        assert "B) Pilha" in prompt
        assert "Alternativa correta: B" in prompt


class TestExplicarQuestao:
    def test_sem_chave_configurada_levanta_erro(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.assistente_ia.GEMINI_API_KEY", "", raising=False
        )
        with pytest.raises(AssistenteIAIndisponivelError):
            asyncio.run(explicar_questao(questao_exemplo()))
