"""Endpoints HTTP do recurso tarefas."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.tarefa import (
    StatusTarefa,
    TarefaCreate,
    TarefaResponse,
    TarefaUpdate,
)
from app.services import tarefas as servico

router = APIRouter(prefix="/tarefas", tags=["Tarefas"])

FiltroStatus = Annotated[
    StatusTarefa | None,
    Query(alias="status", description="Filtra as tarefas pelo status informado."),
]


@router.get("", response_model=list[TarefaResponse])
def listar_tarefas(status_filtro: FiltroStatus = None) -> list[dict]:
    """Lista as tarefas, com filtro opcional por status (Query Parameter)."""
    return servico.listar(status_filtro)


@router.get("/resumo")
def resumo_das_tarefas() -> dict:
    """Devolve o resumo agregado das tarefas."""
    return servico.resumo()


@router.get("/{tarefa_id}", response_model=TarefaResponse)
def buscar_tarefa(tarefa_id: int) -> dict:
    """Busca uma tarefa pelo id (Path Parameter)."""
    try:
        return servico.buscar(tarefa_id)
    except servico.TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)
        ) from erro


@router.post("", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
def criar_tarefa(dados: TarefaCreate) -> dict:
    """Cria uma nova tarefa."""
    return servico.criar(dados)


@router.put("/{tarefa_id}", response_model=TarefaResponse)
def substituir_tarefa(tarefa_id: int, dados: TarefaCreate) -> dict:
    """Substitui todos os campos de uma tarefa existente."""
    try:
        return servico.substituir(tarefa_id, dados)
    except servico.TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)
        ) from erro


@router.patch("/{tarefa_id}", response_model=TarefaResponse)
def atualizar_tarefa(tarefa_id: int, dados: TarefaUpdate) -> dict:
    """Atualiza parcialmente uma tarefa existente."""
    try:
        return servico.atualizar(tarefa_id, dados)
    except servico.TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)
        ) from erro


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tarefa(tarefa_id: int) -> None:
    """Remove uma tarefa existente."""
    try:
        servico.remover(tarefa_id)
    except servico.TarefaNaoEncontradaError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)
        ) from erro
