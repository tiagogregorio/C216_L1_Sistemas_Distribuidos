"""Endpoint de verificacao de disponibilidade da aplicacao."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def health_check() -> dict:
    """Confirma que a aplicacao esta no ar."""
    return {"status": "ok"}
