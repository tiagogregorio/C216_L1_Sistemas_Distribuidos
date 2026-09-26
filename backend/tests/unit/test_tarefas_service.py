import pytest

from app.schemas.tarefa import TarefaCreate, TarefaUpdate
from app.services import tarefas as servico


def test_normalizar_titulo_remove_espacos_extras():
    assert servico.normalizar_titulo("  estudar    pytest  ") == "estudar pytest"


def test_normalizar_titulo_rejeita_titulo_vazio():
    with pytest.raises(ValueError, match="nao pode ser vazio"):
        servico.normalizar_titulo("     ")


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("baixa", "baixa"),
        ("MEDIA", "media"),
        ("  Alta  ", "alta"),
    ],
)
def test_validar_prioridade_aceita_valores_validos(entrada, esperado):
    assert servico.validar_prioridade(entrada) == esperado


@pytest.mark.parametrize("entrada", ["urgente", "", "altissima"])
def test_validar_prioridade_rejeita_valores_invalidos(entrada):
    with pytest.raises(ValueError, match="Prioridade invalida"):
        servico.validar_prioridade(entrada)


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
    assert servico.calcular_progresso(total, concluidas) == esperado


def test_calcular_progresso_rejeita_concluidas_maior_que_total():
    with pytest.raises(ValueError, match="maior que o total"):
        servico.calcular_progresso(2, 5)


@pytest.mark.parametrize(
    ("tarefa", "esperado"),
    [
        ({"status": "concluida"}, True),
        ({"status": "pendente"}, False),
        ({}, False),
    ],
)
def test_esta_concluida_identifica_o_status(tarefa, esperado):
    assert servico.esta_concluida(tarefa) is esperado


def test_resumir_tarefas_agrega_os_dados_da_fixture(tarefas_exemplo):
    resumo = servico.resumir_tarefas(tarefas_exemplo)

    assert resumo["total"] == 4
    assert resumo["concluidas"] == 2
    assert resumo["progresso"] == 50.0


def test_criar_gera_ids_sequenciais():
    primeira = servico.criar(TarefaCreate(titulo="Primeira tarefa"))
    segunda = servico.criar(TarefaCreate(titulo="Segunda tarefa"))

    assert primeira["id"] == 1
    assert segunda["id"] == 2


def test_criar_normaliza_titulo_e_prioridade():
    tarefa = servico.criar(TarefaCreate(titulo="  ler   docs  ", prioridade="alta"))

    assert tarefa["titulo"] == "ler docs"
    assert tarefa["prioridade"] == "alta"
    assert tarefa["status"] == "pendente"


def test_buscar_id_inexistente_levanta_erro_de_dominio():
    with pytest.raises(servico.TarefaNaoEncontradaError, match="99"):
        servico.buscar(99)


def test_substituir_troca_o_objeto_inteiro():
    criada = servico.criar(TarefaCreate(titulo="Titulo antigo", prioridade="alta"))

    substituida = servico.substituir(criada["id"], TarefaCreate(titulo="Titulo novo"))

    assert substituida["titulo"] == "Titulo novo"
    assert substituida["prioridade"] == "media"


def test_atualizar_altera_apenas_os_campos_enviados():
    criada = servico.criar(TarefaCreate(titulo="Titulo antigo", prioridade="alta"))

    atualizada = servico.atualizar(criada["id"], TarefaUpdate(status="concluida"))

    assert atualizada["status"] == "concluida"
    assert atualizada["titulo"] == "Titulo antigo"
    assert atualizada["prioridade"] == "alta"


def test_remover_apaga_a_tarefa():
    criada = servico.criar(TarefaCreate(titulo="Tarefa descartavel"))

    servico.remover(criada["id"])

    assert servico.listar() == []


def test_listar_filtra_por_status():
    servico.criar(TarefaCreate(titulo="Tarefa pendente"))
    servico.criar(TarefaCreate(titulo="Tarefa pronta", status="concluida"))

    pendentes = servico.listar("pendente")

    assert len(pendentes) == 1
    assert pendentes[0]["titulo"] == "Tarefa pendente"
