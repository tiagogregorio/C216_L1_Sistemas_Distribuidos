COMPOSE = docker compose

.PHONY: help up down down-v build restart logs \
        back-sh db-sh front-sh db-upgrade db-downgrade db-history \
        seed test test-back test-front lint format check-all clean

help: ## Mostra os comandos disponiveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# === Docker ===
up: ## Sobe os containers (db + backend + frontend)
	$(COMPOSE) up -d --build

down: ## Para os containers
	$(COMPOSE) down

down-v: ## Para os containers e remove volumes
	$(COMPOSE) down -v

build: ## Rebuild sem cache
	$(COMPOSE) build --no-cache

restart: ## Reinicia os containers
	$(COMPOSE) restart

logs: ## Mostra logs em tempo real
	$(COMPOSE) logs -f

# === Shell ===
back-sh: ## Abre shell no backend
	$(COMPOSE) exec backend bash

db-sh: ## Abre psql no banco
	$(COMPOSE) exec db psql -U postgres -d enade_platform

front-sh: ## Abre shell no frontend
	$(COMPOSE) exec frontend sh

# === Banco de dados ===
db-upgrade: ## Aplica migracoes pendentes
	$(COMPOSE) exec backend alembic upgrade head

db-downgrade: ## Reverte ultima migracao
	$(COMPOSE) exec backend alembic downgrade -1

db-history: ## Mostra historico de migracoes
	$(COMPOSE) exec backend alembic history

# === Seed ===
seed: ## Popula o banco com questoes do ENADE
	$(COMPOSE) exec backend python -m app.seed

# === Qualidade ===
test: test-back test-front ## Roda todos os testes

test-back: ## Roda testes do backend
	$(COMPOSE) exec backend pytest

test-front: ## Roda testes do frontend
	$(COMPOSE) exec frontend sh -c "cd /app && npx vitest run" 2>/dev/null || \
		cd frontend && npx vitest run

lint: ## Verifica lint com ruff (backend) e biome (frontend)
	$(COMPOSE) exec backend ruff check .
	cd frontend && npx @biomejs/biome check src/

format: ## Formata codigo
	$(COMPOSE) exec backend ruff format .
	cd frontend && npx @biomejs/biome format --write src/

check-all: lint test ## Roda lint e testes
