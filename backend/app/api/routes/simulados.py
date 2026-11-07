"""Rotas REST dos recursos simulado e dashboard."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.questao import QuestaoRepository
from app.repositories.simulado import SimuladoRepository
from app.schemas.questao import QuestaoResponse
from app.schemas.simulado import (
    DashboardResponse,
    SimuladoCreate,
    SimuladoDetalhe,
    SimuladoResponse,
    SimuladoSubmit,
)
from app.services.simulados import (
    QuestoesInsuficientesError,
    SimuladoJaFinalizadoError,
    SimuladoNaoEncontradoError,
    SimuladoService,
)

router = APIRouter(prefix="/simulados", tags=["Simulados"])


def get_simulado_service(db: Session = Depends(get_db)) -> SimuladoService:
    return SimuladoService(SimuladoRepository(db), QuestaoRepository(db))


@router.get("/", response_model=list[SimuladoResponse])
def listar_simulados(
    service: SimuladoService = Depends(get_simulado_service),
):
    """Lista todos os simulados, do mais recente ao mais antigo."""
    return service.listar()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(service: SimuladoService = Depends(get_simulado_service)):
    """Retorna estatisticas gerais de desempenho."""
    return service.dashboard()


@router.post("/", status_code=201)
def criar_simulado(
    dados: SimuladoCreate,
    service: SimuladoService = Depends(get_simulado_service),
):
    """Gera um novo simulado com questoes aleatorias."""
    try:
        simulado, questao_ids = service.criar(dados)
        return {
            "simulado": SimuladoResponse.model_validate(simulado),
            "questao_ids": questao_ids,
        }
    except QuestoesInsuficientesError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{simulado_id}", response_model=SimuladoDetalhe)
def buscar_simulado(
    simulado_id: int,
    service: SimuladoService = Depends(get_simulado_service),
):
    """Retorna um simulado com a lista de respostas."""
    try:
        return service.buscar(simulado_id)
    except SimuladoNaoEncontradoError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{simulado_id}/questoes", response_model=list[QuestaoResponse])
def questoes_do_simulado(
    simulado_id: int,
    service: SimuladoService = Depends(get_simulado_service),
    db: Session = Depends(get_db),
):
    """Retorna as questoes associadas a um simulado (para responder)."""
    try:
        simulado = service.buscar(simulado_id)
    except SimuladoNaoEncontradoError as e:
        raise HTTPException(status_code=404, detail=str(e))

    questao_repo = QuestaoRepository(db)
    questao_ids = [r.questao_id for r in simulado.respostas]

    if not questao_ids:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma questao associada a este simulado.",
        )

    questoes = [questao_repo.buscar_por_id(qid) for qid in questao_ids]
    return [q for q in questoes if q is not None]


@router.post("/{simulado_id}/submeter", response_model=SimuladoDetalhe)
def submeter_respostas(
    simulado_id: int,
    dados: SimuladoSubmit,
    service: SimuladoService = Depends(get_simulado_service),
):
    """Recebe as respostas, corrige automaticamente e devolve o resultado."""
    try:
        return service.submeter(simulado_id, dados)
    except SimuladoNaoEncontradoError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SimuladoJaFinalizadoError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{simulado_id}", status_code=204)
def remover_simulado(
    simulado_id: int,
    service: SimuladoService = Depends(get_simulado_service),
):
    """Remove um simulado e todas as suas respostas."""
    try:
        service.remover(simulado_id)
    except SimuladoNaoEncontradoError as e:
        raise HTTPException(status_code=404, detail=str(e))
