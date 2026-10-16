"""Configuracoes da aplicacao lidas de variaveis de ambiente."""

import os

# Dentro do Docker Compose o host do banco e "db" (nome do servico).
# O valor padrao abaixo serve apenas para execucao local fora dos containers.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/sistemas_distribuidos",
)
