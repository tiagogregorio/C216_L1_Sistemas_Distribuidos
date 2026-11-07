"""Schemas Pydantic para validacao de simulados e respostas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SimuladoCreate(BaseModel):
    """Corpo aceito para gerar um novo simulado."""

    nome: str = Field(min_length=3, max_length=120)
    quantidade: int = Field(ge=1, le=50, default=10)
    ano: int | None = Field(default=None, ge=2004, le=2030)
    tipo: str | None = Field(default=None, pattern=r"^(FG|CE)$")


class RespostaSubmit(BaseModel):
    """Uma resposta individual enviada pelo usuario."""

    questao_id: int
    alternativa_escolhida: str = Field(pattern=r"^[A-E]$")


class SimuladoSubmit(BaseModel):
    """Corpo enviado ao finalizar um simulado."""

    respostas: list[RespostaSubmit] = Field(min_length=1)


class RespostaResponse(BaseModel):
    """Representacao de uma resposta dentro do resultado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    questao_id: int
    alternativa_escolhida: str | None
    correta: bool | None


class SimuladoResponse(BaseModel):
    """Representacao completa de um simulado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    criado_em: datetime
    finalizado: bool
    total_questoes: int
    acertos: int | None
    nota: float | None


class SimuladoDetalhe(SimuladoResponse):
    """Simulado com a lista de respostas incluida."""

    respostas: list[RespostaResponse] = []


class DashboardResponse(BaseModel):
    """Estatisticas gerais de desempenho do usuario."""

    total_simulados: int
    simulados_finalizados: int
    media_nota: float | None
    total_questoes_respondidas: int
    total_acertos: int
    taxa_acerto_geral: float
    desempenho_por_ano: list[dict]
    desempenho_por_tipo: list[dict]
