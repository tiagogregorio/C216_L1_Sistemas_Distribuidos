"""Inicializacao da aplicacao FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, questoes, simulados
from app.core.config import CORS_ORIGINS

app = FastAPI(
    title="ENADE Study Platform",
    description="API para o ENADE.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(questoes.router)
app.include_router(simulados.router)
