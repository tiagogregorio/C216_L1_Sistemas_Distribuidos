POETRY = poetry

.PHONY: help install run test test-fast lint lint-fix format format-check check up down down-v build restart logs back-sh db-sh clean

help:
	@echo "Comandos disponiveis:"
	@echo "  make install      - instala as dependencias do backend"
	@echo "  make run          - roda o servidor de desenvolvimento (sem Docker)"
	@echo "  make test         - roda os testes automatizados"
	@echo "  make test-fast    - roda os testes parando no primeiro erro"
	@echo "  make lint         - verifica o codigo com o Ruff"
	@echo "  make lint-fix     - corrige automaticamente o que o Ruff conseguir"
	@echo "  make format       - formata o codigo com o Ruff"
	@echo "  make format-check - confere a formatacao sem alterar arquivos"
	@echo "  make check        - roda lint, formatacao e testes (as checagens do CI)"
	@echo "  make up           - sobe os containers em background"
	@echo "  make down         - para e remove os containers"
	@echo "  make down-v       - para os containers e apaga os volumes (perde dados do banco)"
	@echo "  make build        - reconstroi as imagens Docker"
	@echo "  make restart      - reinicia todos os containers"
	@echo "  make logs         - acompanha os logs do backend em tempo real"
	@echo "  make back-sh      - abre um shell dentro do container do backend"
	@echo "  make db-sh        - abre o psql dentro do container do banco"
	@echo "  make clean        - remove cache e arquivos temporarios do Python"

install:
	cd backend && $(POETRY) install

run:
	cd backend && $(POETRY) run uvicorn main:app --reload

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
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

build:
	docker compose up -d --build

restart:
	docker compose restart

logs:
	docker compose logs -f backend

back-sh:
	docker compose exec backend sh

db-sh:
	docker compose exec db psql -U postgres -d sistemas_distribuidos

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
