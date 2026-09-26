"""Modelos Pydantic usados na validacao de entrada e saida das tarefas."""

from typing import Literal

from pydantic import BaseModel, Field

Prioridade = Literal["baixa", "media", "alta"]
StatusTarefa = Literal["pendente", "concluida"]


class TarefaBase(BaseModel):
    """Campos comuns a todas as representacoes de uma tarefa."""

    titulo: str = Field(min_length=3, max_length=80)
    prioridade: Prioridade = "media"
    status: StatusTarefa = "pendente"


class TarefaCreate(TarefaBase):
    """Corpo aceito na criacao (POST) e na substituicao completa (PUT)."""


class TarefaUpdate(BaseModel):
    """Corpo aceito na atualizacao parcial (PATCH): todos os campos opcionais."""

    titulo: str | None = Field(default=None, min_length=3, max_length=80)
    prioridade: Prioridade | None = None
    status: StatusTarefa | None = None


class TarefaResponse(TarefaBase):
    """Representacao devolvida pela API."""

    id: int
