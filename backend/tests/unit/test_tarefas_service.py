import pytest

from tarefas import (
    calcular_progresso,
    esta_concluida,
    normalizar_titulo,
    resumir_tarefas,
    validar_prioridade,
)


def test_normalizar_titulo_remove_espacos_extras():
    assert normalizar_titulo("  estudar    pytest  ") == "estudar pytest"


def test_normalizar_titulo_rejeita_titulo_vazio():
    with pytest.raises(ValueError, match="nao pode ser vazio"):
        normalizar_titulo("     ")


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("baixa", "baixa"),
        ("MEDIA", "media"),
        ("  Alta  ", "alta"),
    ],
)
def test_validar_prioridade_aceita_valores_validos(entrada, esperado):
    assert validar_prioridade(entrada) == esperado


@pytest.mark.parametrize("entrada", ["urgente", "", "altissima"])
def test_validar_prioridade_rejeita_valores_invalidos(entrada):
    with pytest.raises(ValueError, match="Prioridade invalida"):
        validar_prioridade(entrada)


@pytest.mark.parametrize(
    ("total", "concluidas", "esperado"),
    [
        (0, 0, 0.0),
        (4, 2, 50.0),
        (3, 1, 33.33),
        (5, 5, 100.0),
    ],
)
def test_calcular_progresso_retorna_percentual_correto(total, concluidas, esperado):
    assert calcular_progresso(total, concluidas) == esperado


def test_calcular_progresso_rejeita_concluidas_maior_que_total():
    with pytest.raises(ValueError, match="maior que o total"):
        calcular_progresso(2, 5)


@pytest.mark.parametrize(
    ("tarefa", "esperado"),
    [
        ({"status": "concluida"}, True),
        ({"status": "pendente"}, False),
        ({}, False),
    ],
)
def test_esta_concluida_identifica_o_status(tarefa, esperado):
    assert esta_concluida(tarefa) is esperado


def test_resumir_tarefas_agrega_os_dados_da_fixture(tarefas_exemplo):
    resumo = resumir_tarefas(tarefas_exemplo)

    assert resumo["total"] == 4
    assert resumo["concluidas"] == 2
    assert resumo["progresso"] == 50.0
