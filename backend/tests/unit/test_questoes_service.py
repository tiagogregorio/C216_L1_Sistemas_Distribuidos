"""Testes unitarios do servico de questoes."""

import pytest

from app.services.questoes import (
    normalizar_enunciado,
    validar_dificuldade,
    validar_resposta,
    validar_tipo,
)


class TestNormalizarEnunciado:
    def test_remove_espacos_duplicados(self):
        assert normalizar_enunciado("  texto   com   espacos  ") == "texto com espacos"

    def test_enunciado_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            normalizar_enunciado("   ")


class TestValidarTipo:
    def test_tipo_valido_fg(self):
        assert validar_tipo("fg") == "FG"

    def test_tipo_valido_ce(self):
        assert validar_tipo("CE") == "CE"

    def test_tipo_invalido(self):
        with pytest.raises(ValueError, match="Tipo invalido"):
            validar_tipo("XX")


class TestValidarResposta:
    @pytest.mark.parametrize("entrada,esperado", [("a", "A"), ("B", "B"), ("e", "E")])
    def test_resposta_valida(self, entrada, esperado):
        assert validar_resposta(entrada) == esperado

    def test_resposta_invalida(self):
        with pytest.raises(ValueError, match="Resposta invalida"):
            validar_resposta("F")


class TestValidarDificuldade:
    def test_none_retorna_none(self):
        assert validar_dificuldade(None) is None

    def test_dificuldade_valida(self):
        assert validar_dificuldade("FACIL") == "facil"
        assert validar_dificuldade("medio") == "medio"

    def test_dificuldade_invalida(self):
        with pytest.raises(ValueError, match="Dificuldade invalida"):
            validar_dificuldade("expert")
