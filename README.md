# ENADE Study Platform

Plataforma de estudos para o ENADE de Engenharia de Computacao, com quiz interativo inspirado no Show do Milhao, cronometro por questao, correcao automatica e dashboard de desempenho.

Projeto Final da disciplina **C216 - Sistemas Distribuidos** (Inatel, 2026/2).

## Funcionalidades

- **Banco de questoes**: CRUD completo de questoes objetivas do ENADE, com filtros por ano, tipo (Formacao Geral / Componente Especifico), dificuldade e assunto.
- **Simulados interativos**: geracao de simulados com questoes aleatorias, cronometro por questao, interface inspirada no Show do Milhao e correcao automatica com nota.
- **Dashboard de desempenho**: estatisticas de acertos por ano, por tipo, taxa geral, media dos simulados e tempo medio por questao.
- **Seed com questoes reais**: 15 questoes objetivas extraidas das provas do ENADE 2014 e 2019 com gabarito oficial.
- **Cadastro manual**: possibilidade de incluir novas questoes pelo formulario do frontend.

## Stack

| Camada     | Tecnologia                          |
|------------|-------------------------------------|
| Backend    | FastAPI, SQLAlchemy, Alembic, Poetry|
| Frontend   | React, Vite, Tailwind CSS, Biome   |
| Banco      | PostgreSQL 16                       |
| Infra      | Docker, Docker Compose              |
| Testes     | Pytest, Vitest, Playwright          |
| CI         | GitHub Actions                      |
| Lint       | Ruff (backend), Biome (frontend)    |

## Estrutura do Projeto

```
.
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Rotas REST (health, questoes, simulados)
│   │   ├── core/config.py       # Variaveis de ambiente
│   │   ├── database/            # Engine, sessao e base ORM
│   │   ├── models/              # Modelos SQLAlchemy (Questao, Simulado, Resposta)
│   │   ├── repositories/        # Acesso ao banco de dados
│   │   ├── schemas/             # Schemas Pydantic (validacao)
│   │   ├── services/            # Regras de negocio
│   │   ├── seed.py              # Script de seed com questoes do ENADE
│   │   └── main.py              # Aplicacao FastAPI
│   ├── alembic/                 # Migracoes do banco de dados
│   ├── tests/
│   │   ├── unit/                # Testes unitarios (validacoes)
│   │   └── integration/         # Testes de integracao (endpoints)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, QuestaoForm, QuizQuestao
│   │   ├── pages/               # Dashboard, Questoes, NovoSimulado, Simulado, Historico
│   │   ├── services/api.js      # Camada HTTP
│   │   ├── validation.js        # Validacoes do frontend
│   │   ├── App.jsx              # Componente raiz com navegacao
│   │   └── main.jsx             # Entry point
│   ├── tests/
│   │   ├── e2e/                 # Testes E2E com Playwright
│   │   ├── App.test.jsx         # Testes de componente
│   │   └── validation.test.js   # Testes de validacao
│   ├── Dockerfile
│   ├── nginx.conf
│   └── playwright.config.js
├── .github/workflows/           # CI: backend.yml e frontend.yml
├── docker-compose.yml           # Orquestracao dos 3 servicos
├── Makefile                     # Comandos documentados
├── .env.example                 # Variaveis de ambiente (sem segredos)
└── README.md
```

## Pre-requisitos

- Docker e Docker Compose
- Node.js 22+ (para desenvolvimento local do frontend)
- Python 3.12+ e Poetry (para desenvolvimento local do backend)

## Variaveis de Ambiente

Copie o `.env.example` para `.env` na raiz do projeto:

```bash
cp .env.example .env
```

| Variavel           | Descricao                     | Padrao                    |
|--------------------|-------------------------------|---------------------------|
| POSTGRES_USER      | Usuario do PostgreSQL         | postgres                  |
| POSTGRES_PASSWORD  | Senha do PostgreSQL           | postgres                  |
| POSTGRES_DB        | Nome do banco                 | enade_platform            |
| FRONTEND_URL       | URL do frontend (CORS)        | http://localhost:5173      |
| CORS_ORIGINS       | Origens permitidas (CORS)     | http://localhost:5173,...  |
| VITE_API_URL       | URL da API para o frontend    | http://localhost:8000      |
| GEMINI_API_KEY     | Chave da API do Google Gemini (opcional, para o "Assistente IA") | vazio |
| GEMINI_MODEL       | Modelo do Gemini usado pelo assistente | gemini-2.5-flash |

## Como Executar

### Com Docker Compose (recomendado)

```bash
# 1. Copie as variaveis de ambiente
cp .env.example .env

# 2. Sobe os 3 servicos (db, backend, frontend)
make up

# 3. Aplica as migracoes do banco
make db-upgrade

# 4. Popula com questoes do ENADE
make seed

# 5. Acesse no navegador
# Frontend: http://localhost:3000
# API Swagger: http://localhost:8000/docs
```

### Desenvolvimento Local

```bash
# Sobe db + backend via Docker
make up

# Frontend com hot reload
cd frontend && npm install && npm run dev
# Acesse: http://localhost:5173
```

## Comandos do Makefile

| Comando          | Descricao                                      |
|------------------|-------------------------------------------------|
| `make help`      | Mostra todos os comandos disponiveis            |
| `make up`        | Sobe os containers (db + backend + frontend)    |
| `make down`      | Para os containers                              |
| `make down-v`    | Para containers e remove volumes                |
| `make build`     | Rebuild sem cache                               |
| `make logs`      | Mostra logs em tempo real                       |
| `make db-upgrade`| Aplica migracoes pendentes                      |
| `make db-history`| Mostra historico de migracoes                   |
| `make seed`      | Popula o banco com questoes do ENADE            |
| `make test`      | Roda todos os testes (backend + frontend)       |
| `make test-back` | Roda testes do backend (Pytest)                 |
| `make lint`      | Verifica lint (Ruff + Biome)                    |
| `make format`    | Formata codigo (Ruff + Biome)                   |
| `make back-sh`   | Abre shell no backend                           |
| `make db-sh`     | Abre psql no banco                              |

## Migracoes

```bash
make db-upgrade    # Aplicar migracoes
make db-downgrade  # Reverter ultima
make db-history    # Ver historico
```

Migracoes existentes:
1. `56d0baaf5b21` - Cria tabelas questoes, simulados e respostas
2. `a1b2c3d4e5f6` - Adiciona campos dificuldade e tempo de resposta

## Testes

```bash
# Todos os testes
make test

# Backend (30 testes: unitarios + integracao)
make test-back

# Frontend (13 testes com Vitest)
cd frontend && npx vitest run

# E2E com Playwright
cd frontend && npx playwright test
```

## Endpoints da API

### Health
| Metodo | Rota       | Descricao             |
|--------|------------|-----------------------|
| GET    | /health    | Status da API         |

### Questoes
| Metodo | Rota                | Descricao                     |
|--------|---------------------|-------------------------------|
| GET    | /questoes/          | Lista questoes com filtros    |
| POST   | /questoes/          | Cadastra nova questao         |
| GET    | /questoes/resumo    | Estatisticas do banco         |
| GET    | /questoes/anos      | Anos disponiveis              |
| GET    | /questoes/cobertura | Quantas questoes ja foram respondidas (modo sem repetir) |
| POST   | /questoes/cobertura/reiniciar | Inicia um novo ciclo de cobertura |
| POST   | /questoes/{id}/assistente-ia | Explicacao da questao via Gemini |
| GET    | /questoes/{id}      | Busca questao por ID          |
| PUT    | /questoes/{id}      | Substitui questao             |
| PATCH  | /questoes/{id}      | Atualiza parcialmente         |
| DELETE | /questoes/{id}      | Remove questao                |

### Simulados
| Metodo | Rota                           | Descricao                      |
|--------|--------------------------------|--------------------------------|
| GET    | /simulados/                    | Lista simulados                |
| POST   | /simulados/                    | Gera novo simulado             |
| GET    | /simulados/dashboard           | Estatisticas de desempenho     |
| GET    | /simulados/relatorio           | Relatorio de revisao (questoes erradas, prioridades) |
| GET    | /simulados/{id}                | Detalhes do simulado           |
| GET    | /simulados/{id}/questoes       | Questoes do simulado           |
| POST   | /simulados/{id}/submeter       | Submete respostas e corrige    |
| DELETE | /simulados/{id}                | Remove simulado                |

## Video de Demonstracao

[Link para o video de demonstracao](https://link-do-video-aqui)

## Autor

**Tiago R. Gregorio** - Engenharia de Computacao, Inatel (2026/2)
