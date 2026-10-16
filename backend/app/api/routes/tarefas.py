"""Endpoints HTTP do recurso tarefas."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.tarefa import TarefaRepository
from app.schemas.tarefa import (
    StatusTarefa,
    TarefaCreate,
    TarefaResponse,
    TarefaUpdate,
)
from app.services.tarefas import TarefaNaoEncontradaError, TarefaService

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])

NAO_ENCONTRADA = "Tarefa nao encontrada"


def get_tarefa_service(db: Annotated[Session, Depends(get_db)]) -> TarefaService:
    """Monta o service com o repositorio ligado a sessao da requisicao."""
    return TarefaService(TarefaRepository(db))


ServiceDep = Annotated[TarefaService, Depends(get_tarefa_service)]
FiltroStatus = Annotated[
    StatusTarefa | None,
    Query(alias="status", description="Filtra as tarefas pelo status informado."),
]


@router.get("", response_model=list[TarefaResponse])
def listar_tarefas(service: ServiceDep, status_filtro: FiltroStatus = None):
    """Lista as tarefas, com filtro opcional por status (Query Parameter)."""
    return service.listar(status_filtro)


@router.get("/resumo")
def resumo_das_tarefas(service: ServiceDep) -> dict:
    """Devolve o resumo agregado, calculado no banco."""
    return service.resumo()


@router.get("/{tarefa_id}", response_model=TarefaResponse)
def buscar_tarefa(tarefa_id: int, service: ServiceDep):
    """Busca uma tarefa pelo id (Path Parameter)."""
    try:
        return service.buscar(tarefa_id)
    except TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADA
        ) from erro


@router.post("", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
def criar_tarefa(dados: TarefaCreate, service: ServiceDep):
    """Cria uma nova tarefa, persistida no PostgreSQL."""
    return service.criar(dados)


@router.put("/{tarefa_id}", response_model=TarefaResponse)
def substituir_tarefa(tarefa_id: int, dados: TarefaCreate, service: ServiceDep):
    """Substitui todos os campos de uma tarefa existente."""
    try:
        return service.substituir(tarefa_id, dados)
    except TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADA
        ) from erro


@router.patch("/{tarefa_id}", response_model=TarefaResponse)
def atualizar_tarefa(tarefa_id: int, dados: TarefaUpdate, service: ServiceDep):
    """Atualiza parcialmente uma tarefa existente."""
    try:
        return service.atualizar(tarefa_id, dados)
    except TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADA
        ) from erro


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tarefa(tarefa_id: int, service: ServiceDep) -> None:
    """Remove uma tarefa existente."""
    try:
        service.remover(tarefa_id)
    except TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NAO_ENCONTRADA
        ) from erro
