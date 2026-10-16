"""Testes unitarios das funcoes puras e da classe TarefaService."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models.tarefa import Tarefa  # noqa: F401
from app.repositories.tarefa import TarefaRepository
from app.schemas.tarefa import TarefaCreate, TarefaUpdate
from app.services.tarefas import (
    TarefaNaoEncontradaError,
    TarefaService,
    calcular_progresso,
    normalizar_titulo,
    validar_prioridade,
)

# ---------- Funcoes puras (nao precisam de banco) ----------


def test_normalizar_titulo_remove_espacos_extras():
    assert normalizar_titulo("  ler   docs  ") == "ler docs"


def test_normalizar_titulo_rejeita_titulo_vazio():
    with pytest.raises(ValueError, match="vazio"):
        normalizar_titulo("   ")


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [("baixa", "baixa"), ("MEDIA", "media"), ("  Alta  ", "alta")],
)
def test_validar_prioridade_aceita_valores_validos(entrada, esperado):
    assert validar_prioridade(entrada) == esperado


@pytest.mark.parametrize("entrada", ["urgente", "", "altissima"])
def test_validar_prioridade_rejeita_valores_invalidos(entrada):
    with pytest.raises(ValueError):
        validar_prioridade(entrada)


@pytest.mark.parametrize(
    ("total", "concluidas", "esperado"),
    [(0, 0, 0.0), (4, 2, 50.0), (3, 1, 33.33), (5, 5, 100.0)],
)
def test_calcular_progresso_retorna_percentual_correto(total, concluidas, esperado):
    assert calcular_progresso(total, concluidas) == esperado


def test_calcular_progresso_rejeita_concluidas_maior_que_total():
    with pytest.raises(ValueError):
        calcular_progresso(3, 5)


# ---------- TarefaService (precisa de sessao SQLite) ----------


@pytest.fixture
def service():
    """Cria um TarefaService com banco SQLite em memoria, isolado."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    repo = TarefaRepository(session)
    yield TarefaService(repo)
    session.close()
    engine.dispose()


def test_criar_gera_ids_sequenciais(service):
    primeira = service.criar(TarefaCreate(titulo="Primeira tarefa"))
    segunda = service.criar(TarefaCreate(titulo="Segunda tarefa"))
    assert segunda.id == primeira.id + 1


def test_criar_normaliza_titulo_e_prioridade(service):
    tarefa = service.criar(TarefaCreate(titulo="  ler   docs  ", prioridade="alta"))
    assert tarefa.titulo == "ler docs"
    assert tarefa.prioridade == "alta"


def test_buscar_id_inexistente_levanta_erro_de_dominio(service):
    with pytest.raises(TarefaNaoEncontradaError, match="99"):
        service.buscar(99)


def test_substituir_troca_o_objeto_inteiro(service):
    criada = service.criar(TarefaCreate(titulo="Titulo antigo", prioridade="alta"))
    atualizada = service.substituir(criada.id, TarefaCreate(titulo="Titulo novo"))
    assert atualizada.titulo == "Titulo novo"
    assert atualizada.prioridade == "media"


def test_atualizar_altera_apenas_os_campos_enviados(service):
    criada = service.criar(TarefaCreate(titulo="Titulo antigo", prioridade="alta"))
    atualizada = service.atualizar(criada.id, TarefaUpdate(prioridade="baixa"))
    assert atualizada.titulo == "Titulo antigo"
    assert atualizada.prioridade == "baixa"


def test_remover_apaga_a_tarefa(service):
    criada = service.criar(TarefaCreate(titulo="Tarefa descartavel"))
    service.remover(criada.id)
    with pytest.raises(TarefaNaoEncontradaError):
        service.buscar(criada.id)


def test_listar_filtra_por_status(service):
    service.criar(TarefaCreate(titulo="Tarefa pendente"))
    service.criar(TarefaCreate(titulo="Tarefa concluida", status="concluida"))
    pendentes = service.listar("pendente")
    assert len(pendentes) == 1
    assert pendentes[0].titulo == "Tarefa pendente"


def test_resumo_reflete_o_banco(service):
    service.criar(TarefaCreate(titulo="A fazer"))
    service.criar(TarefaCreate(titulo="Feita", status="concluida"))
    resumo = service.resumo()
    assert resumo["total"] == 2
    assert resumo["concluidas"] == 1
    assert resumo["progresso"] == 50.0
