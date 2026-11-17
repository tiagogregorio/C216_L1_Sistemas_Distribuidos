"""Rotas REST do recurso questoes."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.questao import QuestaoRepository
from app.schemas.questao import (
    ClassificacaoLote,
    EstatisticasQuestao,
    QuestaoCreate,
    QuestaoResponse,
    QuestaoResumo,
    QuestaoUpdate,
)
from app.services.assistente_ia import (
    AssistenteIAIndisponivelError,
    classificar_lote,
    explicar_questao,
    ia_configurada,
    modelo_ia,
    testar_conexao,
)
from app.services.importacao_pdf import processar_pdf
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


@router.get("/cobertura")
def cobertura_questoes(service: QuestaoService = Depends(get_questao_service)):
    """Retorna quantas questoes do banco ja foram respondidas (modo
    'sem repetir')."""
    return service.cobertura()


@router.post("/cobertura/reiniciar")
def reiniciar_cobertura(service: QuestaoService = Depends(get_questao_service)):
    """Inicia um novo ciclo de cobertura, permitindo refazer 100% das
    questoes do zero no modo 'sem repetir'. Nao apaga nenhum simulado,
    resposta ou estatistica do dashboard."""
    return service.reiniciar_cobertura()


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


@router.get("/{questao_id}/estatisticas", response_model=EstatisticasQuestao)
def estatisticas_questao(
    questao_id: int,
    service: QuestaoService = Depends(get_questao_service),
):
    """Retorna como os usuarios ja responderam esta questao (ajuda 'Universitarios')."""
    try:
        return service.estatisticas(questao_id)
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/importar-pdf")
async def importar_pdf(
    arquivo: UploadFile = File(...),
    ano: int = Form(...),
    inicio_ce: int = Form(1),
):
    """Extrai um rascunho de questoes de um PDF para revisao na interface.

    Nao salva nada no banco: devolve as questoes candidatas (para o
    usuario editar e aprovar uma a uma) e miniaturas de cada pagina (para
    localizar figuras que precisem ser anexadas manualmente).
    """
    if arquivo.content_type != "application/pdf":
        raise HTTPException(status_code=422, detail="Envie um arquivo PDF.")

    conteudo = await arquivo.read()
    try:
        return processar_pdf(conteudo, ano=ano, inicio_ce=inicio_ce)
    except Exception as e:
        raise HTTPException(
            status_code=422, detail=f"Nao foi possivel processar o PDF: {e}"
        )


@router.get("/ia/status")
async def status_ia(testar: bool = False):
    """Informa se a IA (Gemini) esta configurada, sem expor a chave.

    Com ?testar=true faz uma chamada minima ao Gemini para diagnosticar
    chave invalida, modelo inexistente ou limite de uso.
    """
    resposta = {"configurada": ia_configurada(), "modelo": modelo_ia()}
    if testar and resposta["configurada"]:
        resposta["teste"] = await testar_conexao()
    return resposta


@router.post("/classificar-lote")
async def classificar_questoes_em_lote(dados: ClassificacaoLote):
    """Pede ao Gemini assunto e dificuldade de varias questoes de uma vez
    (usado na tela de importacao de PDF, antes de salvar)."""
    try:
        resultados = await classificar_lote([q.model_dump() for q in dados.questoes])
    except AssistenteIAIndisponivelError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"resultados": resultados}


@router.post("/{questao_id}/assistente-ia")
async def assistente_ia_questao(
    questao_id: int,
    service: QuestaoService = Depends(get_questao_service),
):
    """Pede ao assistente de IA (Gemini) uma explicacao curta sobre a questao."""
    try:
        questao = service.buscar(questao_id)
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        explicacao = await explicar_questao(questao)
    except AssistenteIAIndisponivelError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return {"explicacao": explicacao}


@router.post(
    "/",
    response_model=QuestaoResponse,
    response_model_exclude={"pagina_original"},
    status_code=201,
)
def criar_questao(
    dados: QuestaoCreate,
    service: QuestaoService = Depends(get_questao_service),
):
    """Cadastra uma nova questao no banco."""
    try:
        return service.criar(dados)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put(
    "/{questao_id}",
    response_model=QuestaoResponse,
    response_model_exclude={"pagina_original"},
)
def substituir_questao(
    questao_id: int,
    dados: QuestaoCreate,
    service: QuestaoService = Depends(get_questao_service),
):
    """Substitui completamente uma questao existente."""
    try:
        service.buscar(questao_id)
        return service.atualizar(questao_id, QuestaoUpdate(**dados.model_dump()))
    except QuestaoNaoEncontradaError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.patch(
    "/{questao_id}",
    response_model=QuestaoResponse,
    response_model_exclude={"pagina_original"},
)
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
