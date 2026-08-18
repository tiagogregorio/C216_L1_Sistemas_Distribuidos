POETRY = poetry

.PHONY: help install run test lint format

help:
	@echo "Comandos disponiveis:"
	@echo "  make install  - instala as dependencias do backend"
	@echo "  make run      - roda o servidor de desenvolvimento"
	@echo "  make test     - roda os testes automatizados"
	@echo "  make lint     - verifica o codigo com o Ruff"
	@echo "  make format   - formata o codigo com o Ruff"

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