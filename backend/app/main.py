"""Inicializacao da aplicacao FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import FRONTEND_URL

app = FastAPI(
    title="ENADE Study Platform",
    description="API da plataforma de estudos para o ENADE de Engenharia de Computacao.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
