# ENADE Study Platform

Plataforma de estudos para o ENADE de Engenharia de Computacao, com quiz interativo inspirado no Show do Milhao, cronometro por questao, correcao automatica e dashboard de desempenho.

Projeto Final da disciplina **C216 - Sistemas Distribuidos** (Inatel, 2026/2).

## Funcionalidades

- **Banco de questoes (CRUD completo)**: criar, listar com filtros (ano/fonte, tipo, dificuldade, assunto), editar e excluir questoes, com imagem opcional (ex.: circuitos) e nome livre da prova (nao apenas o ano).
- **Importacao de PDF**: envia o PDF da prova, o backend extrai texto/gabarito (`pdftotext`), mostra as questoes encontradas e voce escolhe quais salvar (uma, varias ou todas). Evita duplicadas e guarda a pagina original do PDF ("Ver pagina do PDF").
- **Simulados estilo Show do Milhao**: cronometro por questao, luz girando no numero, efeitos sonoros e musica de fundo (com volume), navegacao voltar/avancar, avanco automatico, botao PARAR (mantem o progresso) e "Continuar" no historico.
- **Tres modos de simulado**: aleatorio, **sem repetir** (barra de cobertura do banco; ao completar 100% e possivel reiniciar o ciclo sem apagar historico) e **manual** (voce marca exatamente as questoes).
- **Ajudas**: Cartas (elimina 1 a 4 alternativas erradas), Universitarios (votacao simulada) e **Assistente IA** (Google Gemini, opcional).
- **Nota transparente**: nota estilo ENADE (nao respondida conta como erro) e segunda metrica "acerto nas respondidas".
- **Dashboard e Relatorio**: desempenho por ano, tipo e assunto, tempo medio e "O que estudar primeiro", alem de lista das questoes erradas.
- **Classificacao automatica por IA**: o Gemini classifica assunto/tipo das questoes importadas (em lotes).
- **Seeds com questoes reais**: ENADE 2014, 2019 e 2023 com gabarito oficial.

## Stack

| Camada     | Tecnologia                          |
|------------|-------------------------------------|
| Backend    | FastAPI, SQLAlchemy, Alembic, Poetry|
| Frontend   | React, Vite, Tailwind CSS, Biome   |
| Banco      | PostgreSQL 16                       |
| IA (opcional) | Google Gemini (apenas no backend) |
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
| GEMINI_API_KEY     | Chave do Gemini (opcional)    | vazio                     |
| GEMINI_MODEL       | Modelo do Gemini              | gemini-2.5-flash          |
| GEMINI_API_KEY     | Chave da API do Google Gemini (opcional, para o "Assistente IA") | vazio |
| GEMINI_MODEL       | Modelo do Gemini usado pelo assistente | gemini-2.5-flash |

## Como Executar

### Com Docker Compose (recomendado)

```bash
# 1. Copie as variaveis de ambiente
cp .env.example .env

# 2. Sobe os 3 servicos (db, backend, frontend)
make up

# 3. Aplica as migracoes do banco (SEMPRE depois do make up)
make db-upgrade

# 4. Popula com questoes do ENADE
make seed
make seed-2023

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
| `make seed`      | Popula o banco com questoes do ENADE 2014/2019  |
| `make seed-2023` | Adiciona as questoes do ENADE 2023 (idempotente) |
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
3. `c3d4e5f6a7b8` - Adiciona imagem a questao
4. `d4e5f6a7b8c9` - Ciclos de cobertura (modo "sem repetir")
5. `e5f6a7b8c9d0` - Guarda quantas questoes foram respondidas no simulado
6. `f6a7b8c9d0e1` - Campo `fonte` (nome livre da prova)
7. `g7b8c9d0e1f2` - Guarda a pagina original do PDF

Para conferir: `docker compose exec backend alembic current` (deve mostrar `g7b8c9d0e1f2 (head)`).
3. `c3d4e5f6a7b8` - Adiciona imagem a questao
4. `d4e5f6a7b8c9` - Adiciona ciclo de cobertura (modo "sem repetir")
5. `e5f6a7b8c9d0` - Adiciona respondidas ao simulado
6. `f6a7b8c9d0e1` - Adiciona fonte (nome livre) a questao

## Testes

```bash
# Todos os testes
make test

# Backend (79 testes Pytest: unitarios + integracao)
make test-back

# Frontend (39 testes Vitest + Testing Library)
cd frontend && npx vitest run

# E2E com Playwright (5 testes; requer a aplicacao rodando via Docker Compose em
# localhost:3000, com migracoes e seed aplicados). Inclui o teste de persistencia
# real: cadastra uma questao pela interface, recarrega, confere na API e remove.
cd frontend
npm ci
npx playwright install chromium
npx playwright test
```

## Importando questoes de novas provas (PDF)

O projeto inclui uma ferramenta semi-automatizada para extrair questoes
objetivas de provas em PDF (ENADE ou similar, como provas do Inatel):

```bash
docker compose exec backend python -m app.tools.extrair_enade \
  /caminho/para/prova.pdf 2024 --inicio-ce 10
```

Isso gera um rascunho `.py`, uma pagina JPEG por folha do PDF (para
localizar figuras) e um relatorio apontando quais questoes precisam de
revisao manual. Depois de revisar o rascunho e decidir quais questoes
precisam de imagem, use `app.tools.imagem_para_data_uri` para converter
um recorte de imagem no formato que o banco espera. Veja os comentarios
no topo de `backend/app/tools/extrair_enade.py` para o passo a passo
completo — a extracao de texto/gabarito e automatica, mas anexar
imagens e revisar o conteudo continua manual, por design.

### Pagina original do PDF, IA e manutencao

- **Ver pagina do PDF**: ao importar, deixe marcada a opcao de anexar a pagina
  original; no simulado aparece o botao "Ver pagina do PDF" para conferir a
  questao como esta na prova. Reimportar um PDF cujas questoes ja existem **nao
  duplica**: so anexa a pagina.
- **IA (Gemini)**: a tela de importacao mostra se a chave esta configurada e
  tem o botao "Testar conexao". Tambem da para diagnosticar pelo navegador em
  `http://localhost:8000/questoes/ia/status?testar=true` (nunca exibe a chave).
  Rode os comandos `docker compose` na raiz do projeto, junto ao arquivo `.env`.
- **Manutencao do banco**: `make limpar-lixo` (rodape/codigo de barras que
  vieram do PDF), `make duplicadas` e `make remover-duplicadas`.

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
| POST   | /questoes/importar-pdf | Extrai rascunho de questoes de um PDF (nao grava) |
| POST   | /questoes/classificar-lote | Assunto e dificuldade de varias questoes via Gemini |
| GET    | /questoes/ia/status | Diz se a IA esta configurada (`?testar=true` testa a chave) |
| GET    | /questoes/{id}      | Busca questao por ID          |
| PUT    | /questoes/{id}      | Substitui questao             |
| PATCH  | /questoes/{id}      | Atualiza parcialmente         |
| DELETE | /questoes/{id}      | Remove questao                |

Tambem: `GET /questoes/cobertura`, `POST /questoes/cobertura/reiniciar`, `GET /questoes/{id}/estatisticas`,
`POST /questoes/importar-pdf`, `POST /questoes/classificar-lote`, `GET /questoes/ia/status`,
`POST /questoes/{id}/assistente-ia`.

### Simulados
| Metodo | Rota                           | Descricao                      |
|--------|--------------------------------|--------------------------------|
| GET    | /simulados/                    | Lista simulados                |
| POST   | /simulados/                    | Gera novo simulado             |
| GET    | /simulados/dashboard           | Estatisticas de desempenho     |
| GET    | /simulados/relatorio           | Relatorio e prioridades        |
| GET    | /simulados/relatorio           | Relatorio de revisao (questoes erradas, prioridades) |
| GET    | /simulados/{id}                | Detalhes do simulado           |
| GET    | /simulados/{id}/questoes       | Questoes do simulado           |
| POST   | /simulados/{id}/submeter       | Submete respostas e corrige    |
| DELETE | /simulados/{id}                | Remove simulado                |

## Assistente de IA (Gemini) - opcional

A chave fica **somente no backend** (arquivo `.env`, que esta no `.gitignore`); o navegador nunca a ve.
Para usar: crie uma chave gratuita em https://aistudio.google.com/apikey, cole em `GEMINI_API_KEY=` no `.env`
e rode `docker compose up -d --build`. Sem chave, a API responde 503 com mensagem clara e todo o resto funciona.
O avaliador pode usar a propria chave da mesma forma.

## Testes e CI

- Backend: `make test-back` (Pytest, SQLite em memoria nas fixtures) e lint `ruff check` + `ruff format --check`.
- Frontend: `make test-front` (Vitest) e lint `biome check src/`.
- E2E Playwright (`frontend/tests/e2e`, 5 testes): rodam contra a aplicacao real em `localhost:3000` (Docker Compose ativo, com PostgreSQL), incluindo o teste de persistencia (frontend -> API -> banco). Nao rodam no CI por exigirem a stack completa. Para outro endereco: `E2E_BASE_URL` e `E2E_API_URL`.
- GitHub Actions: `Backend CI` e `Frontend CI` rodam lint e testes em push e em Pull Request para `main`.

## Video de Demonstracao

[Link para o video de demonstracao](https://link-do-video-aqui)

## Autor

**Tiago R. Gregorio** - Engenharia de Computacao, Inatel (2026/2)
