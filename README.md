# C216_L1_Sistemas_Distribuidos

API de tarefas do laboratório de Sistemas Distribuídos, construída com FastAPI.

## Como rodar o projeto

1. Copie o arquivo de variáveis de ambiente: `cp .env.example .env`
2. Suba os containers: `make build`
3. Acesse a documentação interativa: http://localhost:8000/docs

Para rodar sem Docker: `make install` e depois `make run`.

## Comandos disponíveis

Rode `make help` para ver a lista completa de comandos.

### Nota sobre Docker no Windows

Os alvos de container usam a variável `COMPOSE`, que por padrão vale
`docker compose`. Em ambientes onde o plugin do Compose não é resolvido
(caso de algumas instalações do Docker Desktop no Windows), basta sobrescrever
na chamada, sem alterar o arquivo:

    make COMPOSE=docker-compose build

## Arquitetura

O backend segue uma **arquitetura em camadas**, com responsabilidade única por módulo:

    backend/
    └── app/
        ├── main.py                 # apenas inicializa o FastAPI e inclui os routers
        ├── api/routes/             # camada de apresentação (endpoints HTTP)
        │   ├── health.py
        │   └── tarefas.py
        ├── schemas/                # contratos de entrada e saída (Pydantic)
        │   └── tarefa.py
        └── services/               # regras de negócio e armazenamento
            └── tarefas.py

O fluxo de uma requisição é:

    Requisição HTTP -> router (api/routes) -> service (regras) -> armazenamento

A camada de serviços não conhece HTTP: ela levanta exceções de domínio
(`TarefaNaoEncontradaError`), e cabe ao router traduzi-las em respostas HTTP.

## Endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/` | Verificação de disponibilidade |
| GET | `/tarefas` | Lista as tarefas (aceita `?status=pendente`) |
| GET | `/tarefas/resumo` | Resumo agregado das tarefas |
| GET | `/tarefas/{tarefa_id}` | Busca uma tarefa pelo id |
| POST | `/tarefas` | Cria uma tarefa |
| PUT | `/tarefas/{tarefa_id}` | Substitui todos os campos de uma tarefa |
| PATCH | `/tarefas/{tarefa_id}` | Atualiza parcialmente uma tarefa |
| DELETE | `/tarefas/{tarefa_id}` | Remove uma tarefa |

A documentação interativa fica disponível em `/docs` com a aplicação no ar.

### Exemplo de uso

    curl -X POST http://localhost:8000/tarefas \
      -H "Content-Type: application/json" \
      -d '{"titulo": "Estudar FastAPI", "prioridade": "alta"}'

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

### Organização dos testes

    backend/tests/
    ├── conftest.py              # fixtures compartilhadas
    ├── unit/                    # testam o service isoladamente, sem HTTP
    │   └── test_tarefas_service.py
    └── integration/             # testam os endpoints via TestClient
        └── test_tarefas_routes.py

São 39 casos executados: 24 unitários e 15 de integração. Todos os endpoints
da API são cobertos pelos testes de integração, incluindo os casos de erro
(404 para id inexistente e 422 para payload inválido).

Uma fixture com `autouse=True` zera o armazenamento em memória antes e depois
de cada teste, garantindo que nenhum teste dependa do estado deixado por outro.

### Executando sem o Makefile

    cd backend
    poetry install
    poetry run pytest
    poetry run pytest tests/unit
    poetry run pytest tests/integration
    poetry run ruff check .
    poetry run ruff format --check .

### Executando dentro do container

    make up
    docker compose exec backend poetry run pytest

### Integração contínua

O workflow `.github/workflows/ci-backend.yml` roda a cada `push` e a cada
`pull_request`, em dois jobs paralelos:

- **Lint e formatação (Ruff)** — `ruff check` e `ruff format --check`
- **Testes (Pytest)** — `pytest`, cobrindo unitários e integração

O merge para a branch `aulas` depende desses dois checks passarem, além da
aprovação no code review.
