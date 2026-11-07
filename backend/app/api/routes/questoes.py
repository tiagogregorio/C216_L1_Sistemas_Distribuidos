"""Rotas REST do recurso questoes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.questao import QuestaoRepository
from app.schemas.questao import (
    QuestaoCreate,
    QuestaoResponse,
    QuestaoResumo,
    QuestaoUpdate,
)
from app.services.questoes import QuestaoNaoEncontradaError, QuestaoService

router = APIRouter(prefix="/questoes", tags=["Questoes"])


def get_questao_service(db: Session = Depends(get_db)) -> QuestaoService:
    return QuestaoService(QuestaoRepository(db))


@router.get("/", response_model=list[QuestaoResumo])
def listar_questoes(
    ano: int | None = Query(default=None),
    tipo: str | None = Query(default=None),
    assunto: str | None = Query(default=None),
    dificuldade: str | None = Query(default=None),
    service: QuestaoService = Depends(get_questao_service),
):
    """Lista questoes com filtros opcionais por ano, tipo, assunto e dificuldade."""
    return service.listar(ano=ano, tipo=tipo, assunto=assunto, dificuldade=dificuldade)


@router.get("/resumo")
def resumo_questoes(service: QuestaoService = Depends(get_questao_service)):
    """Retorna estatisticas do banco de questoes."""
    return service.resumo()


@router.get("/anos")
def anos_disponiveis(service: QuestaoService = Depends(get_questao_service)):
    """Retorna a lista de anos com questoes cadastradas."""
    return service.anos_disponiveis()


@router.get("/{questao_id}", response_model=QuestaoResponse)
def buscar_questao(
    questao_id: int,
    service: QuestaoService = Depends(get_questao_service),
):
    """Retorna uma questao pelo ID, incluindo alternativas e gabarito."""
    try:
        return service.buscar(questao_id)
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=QuestaoResponse, status_code=201)
def criar_questao(
    dados: QuestaoCreate,
    service: QuestaoService = Depends(get_questao_service),
):
    """Cadastra uma nova questao no banco."""
    try:
        return service.criar(dados)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("/{questao_id}", response_model=QuestaoResponse)
def substituir_questao(
    questao_id: int,
    dados: QuestaoCreate,
    service: QuestaoService = Depends(get_questao_service),
):
    """Substitui completamente uma questao existente."""
    try:
        service.buscar(questao_id)
        return service.atualizar(
            questao_id, QuestaoUpdate(**dados.model_dump())
        )
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch("/{questao_id}", response_model=QuestaoResponse)
def atualizar_questao(
    questao_id: int,
    dados: QuestaoUpdate,
    service: QuestaoService = Depends(get_questao_service),
):
    """Atualiza parcialmente uma questao existente."""
    try:
        return service.atualizar(questao_id, dados)
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{questao_id}", status_code=204)
def remover_questao(
    questao_id: int,
    service: QuestaoService = Depends(get_questao_service),
):
    """Remove uma questao do banco."""
    try:
        service.remover(questao_id)
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
