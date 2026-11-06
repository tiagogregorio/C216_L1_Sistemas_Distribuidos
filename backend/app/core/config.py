"""Configuracoes centrais da aplicacao."""

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/enade_platform",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
