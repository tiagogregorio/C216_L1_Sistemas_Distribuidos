COMPOSE = docker compose
# -T: sem pseudo-terminal, para os comandos funcionarem igual em qualquer shell
# (Linux, macOS, Git Bash no Windows e CI).
EXEC = $(COMPOSE) exec -T

.PHONY: help setup env up down down-v build restart logs ps \
        back-sh db-sh front-sh db-upgrade db-downgrade db-history db-current db-ultimas \
        seed seed-2023 fix-q10-2023 limpar-lixo duplicadas remover-duplicadas \
        front-install e2e-install test test-back test-front test-e2e \
        lint format check-all

help: ## Mostra os comandos disponiveis
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Inicio rapido ===
setup: env up db-upgrade seed seed-2023 ## Prepara tudo do zero (.env, containers, migracoes e seeds)

env: ## Cria o .env a partir do .env.example (nao sobrescreve um .env existente)
	@test -f .env || cp .env.example .env

# === Docker ===
up: ## Sobe os containers (db + backend + frontend)
	$(COMPOSE) up -d --build

down: ## Para os containers
	$(COMPOSE) down

down-v: ## Para os containers e remove volumes (apaga o banco)
	$(COMPOSE) down -v

build: ## Rebuild sem cache
	$(COMPOSE) build --no-cache

restart: ## Reinicia os containers
	$(COMPOSE) restart

logs: ## Mostra logs em tempo real
	$(COMPOSE) logs -f

ps: ## Mostra o estado dos containers
	$(COMPOSE) ps

# === Shell ===
back-sh: ## Abre shell no backend
	$(COMPOSE) exec backend bash

db-sh: ## Abre psql no banco
	$(COMPOSE) exec db psql -U postgres -d enade_platform

front-sh: ## Abre shell no frontend
	$(COMPOSE) exec frontend sh

# === Banco de dados ===
db-upgrade: ## Aplica migracoes pendentes
	$(EXEC) backend alembic upgrade head

db-downgrade: ## Reverte ultima migracao
	$(EXEC) backend alembic downgrade -1

db-history: ## Mostra historico de migracoes
	$(EXEC) backend alembic history

db-current: ## Mostra a migracao aplicada no banco
	$(EXEC) backend alembic current

db-ultimas: ## Mostra as ultimas questoes gravadas no PostgreSQL
	$(EXEC) db psql -U postgres -d enade_platform -c \
		"SELECT id, ano, numero, tipo, assunto FROM questoes ORDER BY id DESC LIMIT 5;"

# === Seed ===
seed: ## Popula o banco com questoes do ENADE 2014 e 2019
	$(EXEC) backend python -m app.seed

seed-2023: ## Adiciona questoes do ENADE 2023 (nao duplica se ja existirem)
	$(EXEC) backend python -m app.seed_2023

fix-q10-2023: ## Corrige a imagem que faltou na Questao 10 do ENADE 2023
	$(EXEC) backend python -m app.fix_q10_2023

limpar-lixo: ## Remove rodape/codigo de barras do INEP do texto de questoes ja salvas
	$(EXEC) backend python -m app.tools.limpar_lixo_pdf

duplicadas: ## Lista questoes duplicadas (mesmo ano e numero)
	$(EXEC) backend python -m app.tools.duplicadas

remover-duplicadas: ## Remove duplicadas sem simulado (mantem a mais antiga)
	$(EXEC) backend python -m app.tools.duplicadas --remover

# === Qualidade ===
front-install: ## Instala as dependencias do frontend (npm ci)
	cd frontend && npm ci

e2e-install: ## Instala o navegador usado pelo Playwright
	cd frontend && npx playwright install chromium

test: test-back test-front ## Roda os testes do backend e do frontend

test-back: ## Roda testes do backend (Pytest, dentro do container)
	$(EXEC) backend pytest

test-front: ## Roda testes do frontend (Vitest) - requer make front-install
	cd frontend && npx vitest run

test-e2e: ## Roda os testes E2E (Playwright) contra a aplicacao em localhost:3000
	cd frontend && npx playwright test

lint: ## Verifica lint e formatacao: Ruff (backend) e Biome (frontend)
	$(EXEC) backend ruff check --exclude alembic .
	$(EXEC) backend ruff format --check --exclude alembic .
	cd frontend && npx @biomejs/biome check src/

format: ## Formata o codigo: Ruff (backend) e Biome (frontend)
	$(EXEC) backend ruff format --exclude alembic .
	cd frontend && npx @biomejs/biome check --write src/

check-all: lint test ## Roda lint e testes
