POETRY = poetry
COMPOSE ?= docker compose
NPM_FRONTEND = npm --prefix frontend

.PHONY: help install run test test-fast lint lint-fix format format-check check up down down-v build restart logs back-sh db-sh clean db-upgrade db-migration db-current frontend-install frontend-dev frontend-lint frontend-format frontend-format-check frontend-check frontend-test frontend-test-e2e frontend-build check-all

help:
	@echo "Comandos disponiveis:"
	@echo ""
	@echo "  === Backend ==="
	@echo "  make install         - instala as dependencias do backend"
	@echo "  make run             - roda o servidor de desenvolvimento (sem Docker)"
	@echo "  make test            - roda os testes automatizados"
	@echo "  make test-fast       - roda os testes parando no primeiro erro"
	@echo "  make lint            - verifica o codigo com o Ruff"
	@echo "  make lint-fix        - corrige automaticamente o que o Ruff conseguir"
	@echo "  make format          - formata o codigo com o Ruff"
	@echo "  make format-check    - confere a formatacao sem alterar arquivos"
	@echo "  make check           - roda lint, formatacao e testes (as checagens do CI)"
	@echo ""
	@echo "  === Docker ==="
	@echo "  make up              - sobe os containers em background"
	@echo "  make down            - para e remove os containers"
	@echo "  make down-v          - para os containers e apaga os volumes (perde dados do banco)"
	@echo "  make build           - reconstroi as imagens Docker"
	@echo "  make restart         - reinicia todos os containers"
	@echo "  make logs            - acompanha os logs do backend em tempo real"
	@echo "  make back-sh         - abre um shell dentro do container do backend"
	@echo "  make db-sh           - abre o psql dentro do container do banco"
	@echo "  make clean           - remove cache e arquivos temporarios do Python"
	@echo ""
	@echo "  === Banco de Dados ==="
	@echo "  make db-upgrade      - aplica as migrations pendentes no banco"
	@echo "  make db-migration    - gera uma nova migration (use msg='descricao')"
	@echo "  make db-current      - mostra a versao atual do banco"
	@echo ""
	@echo "  === Frontend ==="
	@echo "  make frontend-install     - instala as dependencias do frontend (npm ci)"
	@echo "  make frontend-dev         - servidor de desenvolvimento (Vite)"
	@echo "  make frontend-lint        - verifica o codigo com o Biome"
	@echo "  make frontend-format      - formata o codigo com o Biome"
	@echo "  make frontend-format-check - confere a formatacao sem alterar arquivos"
	@echo "  make frontend-check       - lint + formatacao sem alterar arquivos"
	@echo "  make frontend-test        - roda os testes unitarios e de integracao (Vitest)"
	@echo "  make frontend-test-e2e    - roda os testes E2E (Playwright)"
	@echo "  make frontend-build       - build de producao (Vite)"
	@echo "  make check-all            - roda todas as checagens (backend + frontend)"

install:
	cd backend && $(POETRY) install

run:
	cd backend && $(POETRY) run uvicorn app.main:app --reload

test:
	cd backend && $(POETRY) run pytest

test-fast:
	cd backend && $(POETRY) run pytest -x -q

lint:
	cd backend && $(POETRY) run ruff check .

lint-fix:
	cd backend && $(POETRY) run ruff check . --fix

format:
	cd backend && $(POETRY) run ruff format .

format-check:
	cd backend && $(POETRY) run ruff format --check .

check: lint format-check test

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

down-v:
	$(COMPOSE) down -v

build:
	$(COMPOSE) up -d --build

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f backend

back-sh:
	$(COMPOSE) exec backend sh

db-sh:
	$(COMPOSE) exec db psql -U postgres -d sistemas_distribuidos

db-upgrade:
	$(COMPOSE) exec backend alembic upgrade head

db-migration:
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(msg)"

db-current:
	$(COMPOSE) exec backend alembic current

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

# === Frontend ===

frontend-install:
	$(NPM_FRONTEND) ci

frontend-dev:
	$(NPM_FRONTEND) run dev

frontend-lint:
	$(NPM_FRONTEND) run lint

frontend-format:
	$(NPM_FRONTEND) run format

frontend-format-check:
	$(NPM_FRONTEND) run format:check

frontend-check:
	$(NPM_FRONTEND) run check

frontend-test:
	$(NPM_FRONTEND) run test

frontend-test-e2e:
	$(NPM_FRONTEND) run test:e2e

frontend-build:
	$(NPM_FRONTEND) run build

check-all: check frontend-lint frontend-format-check frontend-test frontend-build frontend-test-e2e
