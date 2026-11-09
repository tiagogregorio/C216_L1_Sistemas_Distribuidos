"""Configuracoes centrais da aplicacao."""

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/enade_platform",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", FRONTEND_URL).split(",")
    if origin.strip()
]

if FRONTEND_URL not in CORS_ORIGINS:
    CORS_ORIGINS.append(FRONTEND_URL)

# Assistente de IA (Google Gemini). A chave fica apenas no backend; o
# frontend nunca tem acesso a ela. Sem GEMINI_API_KEY configurada, o
# endpoint do assistente responde 503 em vez de falhar silenciosamente.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
