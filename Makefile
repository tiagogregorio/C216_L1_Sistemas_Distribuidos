POETRY = poetry

.PHONY: help install run test lint format up down down-v build restart logs back-sh db-sh clean

help:
	@echo "Comandos disponiveis:"
	@echo "  make install  - instala as dependencias do backend"
	@echo "  make run      - roda o servidor de desenvolvimento (sem Docker)"
	@echo "  make test     - roda os testes automatizados"
	@echo "  make lint     - verifica o codigo com o Ruff"
	@echo "  make format   - formata o codigo com o Ruff"
	@echo "  make up       - sobe os containers em background"
	@echo "  make down     - para e remove os containers"
	@echo "  make down-v   - para os containers e apaga os volumes (perde dados do banco)"
	@echo "  make build    - reconstroi as imagens Docker"
	@echo "  make restart  - reinicia todos os containers"
	@echo "  make logs     - acompanha os logs do backend em tempo real"
	@echo "  make back-sh  - abre um shell dentro do container do backend"
	@echo "  make db-sh    - abre o psql dentro do container do banco"
	@echo "  make clean    - remove cache e arquivos temporarios do Python"

install:
	cd backend && $(POETRY) install

run:
	cd backend && $(POETRY) run uvicorn main:app --reload

test:
	cd backend && $(POETRY) run pytest

lint:
	cd backend && $(POETRY) run ruff check .

format:
	cd backend && $(POETRY) run ruff format .

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