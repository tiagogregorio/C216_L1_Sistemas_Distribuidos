"""Schemas Pydantic para validacao de questoes do ENADE."""

from pydantic import BaseModel, ConfigDict, Field

TipoQuestao = str  # "FG" (Formacao Geral) ou "CE" (Componente Especifico)


class QuestaoBase(BaseModel):
    """Campos comuns a todas as representacoes de uma questao."""

    ano: int = Field(ge=2004, le=2030)
    numero: int = Field(ge=1)
    tipo: TipoQuestao = Field(pattern=r"^(FG|CE)$")
    enunciado: str = Field(min_length=10)
    alternativa_a: str = Field(min_length=1)
    alternativa_b: str = Field(min_length=1)
    alternativa_c: str = Field(min_length=1)
    alternativa_d: str = Field(min_length=1)
    alternativa_e: str = Field(min_length=1)
    resposta: str = Field(pattern=r"^[A-E]$")
    assunto: str | None = Field(default=None, max_length=100)
    dificuldade: str | None = Field(default=None, pattern=r"^(facil|medio|dificil)$")
    imagem: str | None = Field(default=None)
    """Imagem (codigo, diagrama, tabela) da questao como data URI base64."""


class QuestaoCreate(QuestaoBase):
    """Corpo aceito na criacao (POST) e na substituicao (PUT)."""


class QuestaoUpdate(BaseModel):
    """Corpo aceito na atualizacao parcial (PATCH)."""

    ano: int | None = Field(default=None, ge=2004, le=2030)
    numero: int | None = Field(default=None, ge=1)
    tipo: TipoQuestao | None = Field(default=None, pattern=r"^(FG|CE)$")
    enunciado: str | None = Field(default=None, min_length=10)
    alternativa_a: str | None = Field(default=None, min_length=1)
    alternativa_b: str | None = Field(default=None, min_length=1)
    alternativa_c: str | None = Field(default=None, min_length=1)
    alternativa_d: str | None = Field(default=None, min_length=1)
    alternativa_e: str | None = Field(default=None, min_length=1)
    resposta: str | None = Field(default=None, pattern=r"^[A-E]$")
    assunto: str | None = Field(default=None, max_length=100)
    dificuldade: str | None = Field(default=None, pattern=r"^(facil|medio|dificil)$")
    imagem: str | None = Field(default=None)


class QuestaoResponse(QuestaoBase):
    """Representacao completa devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class QuestaoResumo(BaseModel):
    """Versao resumida para listagens (sem texto das alternativas)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ano: int
    numero: int
    tipo: str
    assunto: str | None
    dificuldade: str | None


class EstatisticasQuestao(BaseModel):
    """Estatisticas de como os usuarios responderam esta questao ate agora."""

    questao_id: int
    total_respostas: int
    por_alternativa: dict[str, int]
    mais_escolhida: str | None
    taxa_acerto: float | None
