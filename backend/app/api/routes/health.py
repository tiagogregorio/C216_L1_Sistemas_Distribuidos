"""Rota de verificacao de saude da API."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Retorna o status da API."""
    return {"status": "ok", "service": "enade-api"}
