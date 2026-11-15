"""Testes unitarios do assistente de IA (integracao com o Gemini)."""

import asyncio

import pytest

from app.models.questao import Questao
from app.services.assistente_ia import (
    AssistenteIAIndisponivelError,
    _interpretar_classificacao,
    classificar_lote,
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


class TestInterpretarClassificacao:
    def test_normaliza_dificuldade_e_assunto(self):
        texto = (
            '[{"indice": 0, "assunto": "Computação em Nuvem", "dificuldade": "Fácil"},'
            ' {"indice": 1, "assunto": "Tema Novo", "dificuldade": "impossivel"}]'
        )
        resultado = _interpretar_classificacao(texto, 2)
        assert resultado[0] == {
            "assunto": "Computacao em Nuvem",
            "dificuldade": "facil",
        }
        assert resultado[1] == {"assunto": "Tema Novo", "dificuldade": "medio"}

    def test_tolera_markdown_e_lista_embrulhada(self):
        texto = (
            '```json\n{"resultados": [{"indice": 0, "assunto": "Grafos", '
            '"dificuldade": "dificil"}]}\n```'
        )
        assert _interpretar_classificacao(texto, 1)[0] == {
            "assunto": "Grafos",
            "dificuldade": "dificil",
        }

    def test_questao_nao_classificada_fica_com_padrao(self):
        resultado = _interpretar_classificacao("[]", 2)
        assert resultado == [{"assunto": "", "dificuldade": "medio"}] * 2

    def test_json_invalido_levanta_erro(self):
        with pytest.raises(AssistenteIAIndisponivelError):
            _interpretar_classificacao("isto nao e json", 1)


class TestClassificarLote:
    def test_sem_chave_levanta_erro(self, monkeypatch):
        monkeypatch.setattr(
            "app.services.assistente_ia.GEMINI_API_KEY", "", raising=False
        )
        with pytest.raises(AssistenteIAIndisponivelError):
            asyncio.run(classificar_lote([{"enunciado": "x"}]))
