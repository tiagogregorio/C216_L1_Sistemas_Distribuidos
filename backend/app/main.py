"""Inicializacao da aplicacao FastAPI."""

from fastapi import FastAPI

from app.api.routes import health, tarefas

app = FastAPI(
    title="C216 L1 - Sistemas Distribuidos",
    description="API de tarefas do laboratorio de Sistemas Distribuidos.",
    version="0.4.0",
)

app.include_router(health.router)
app.include_router(tarefas.router)
