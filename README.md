# C216_L1_Sistemas_Distribuidos

## Como rodar o projeto

1. Copie o arquivo de variáveis de ambiente: `cp .env.example .env`
2. Suba os containers: `make build`
3. Acesse: http://localhost:8000

## Comandos disponíveis

Rode `make help` para ver a lista completa de comandos.

## Qualidade e testes

O backend usa **Pytest** para os testes e **Ruff** para lint e formatação.
Todos os comandos abaixo são executados a partir da **raiz do projeto**.

| Comando | O que faz |
| --- | --- |
| `make test` | Roda toda a suíte de testes |
| `make test-fast` | Roda os testes parando no primeiro erro |
| `make lint` | Verifica o código com o Ruff |
| `make lint-fix` | Corrige automaticamente o que for possível |
| `make format` | Formata o código com o Ruff |
| `make format-check` | Confere a formatação sem alterar arquivos |
| `make check` | Roda lint + formatação + testes (as mesmas checagens do CI) |

### Executando sem o Makefile

O Poetry está dentro de `backend/`, então é preciso entrar na pasta:

    cd backend
    poetry install
    poetry run pytest
    poetry run ruff check .
    poetry run ruff format --check .

### Executando dentro do container

    make up
    docker compose exec backend poetry run pytest

### Estrutura dos testes

    backend/
    ├── main.py            # camada HTTP (FastAPI)
    ├── tarefas.py         # regras de negocio, sem dependencias externas
    └── tests/
        ├── conftest.py      # fixtures compartilhadas (client e tarefas_exemplo)
        ├── test_tarefas.py  # testes unitarios
        └── test_main.py     # testes de integracao

São 11 funções de teste, que geram **20 casos** por causa da parametrização:
17 unitários e 3 de integração.

### Integração contínua

O workflow `.github/workflows/ci-backend.yml` roda a cada `push` e a cada
`pull_request`, em dois jobs paralelos:

- **Lint e formatação (Ruff)** — `ruff check` e `ruff format --check`
- **Testes (Pytest)** — `pytest`

O merge para a branch `aulas` depende desses dois checks passarem, além da
aprovação no code review.
