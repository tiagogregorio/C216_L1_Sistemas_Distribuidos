# ENADE Study Platform

Plataforma web de estudos para o ENADE de Engenharia de Computacao: um banco de questoes reais das provas, simulados cronometrados no estilo "Show do Milhao" e relatorios que mostram o que estudar primeiro.

Projeto Final da disciplina **C216 - Sistemas Distribuidos** (Inatel, 2026/2).

## Objetivo e tema

As provas do ENADE sao distribuidas em PDF: nao ha como treinar com tempo, repetir so o que ainda nao foi visto ou saber em quais assuntos o desempenho e pior. A plataforma resolve esse problema com:

- um **banco de questoes** objetivas (ENADE 2014, 2019 e 2023) com gabarito oficial;
- **simulados** com cronometro por questao, ajudas e correcao automatica;
- **dashboard e relatorio** de desempenho por ano, tipo e assunto.

## Funcionalidades

- **Banco de questoes (CRUD completo pela interface)**: cadastrar, listar com filtros (ano e tipo), editar e remover questoes, com imagem opcional (ex.: circuitos) e nome livre da prova de origem.
- **Simulados estilo Show do Milhao**: cronometro por questao, efeitos sonoros, musica de fundo com controle de volume, navegacao voltar/avancar, avanco automatico, botao PARAR (mantem o progresso) e "Continuar" no historico.
- **Tres modos de simulado**: aleatorio, **sem repetir** (barra de cobertura do banco; ao chegar a 100% e possivel reiniciar o ciclo sem apagar o historico) e **manual** (o usuario marca exatamente as questoes).
- **Ajudas**: Cartas (elimina de 1 a 4 alternativas erradas), Universitarios (votacao) e Assistente IA (opcional).
- **Nota transparente**: nota estilo ENADE (questao nao respondida conta como erro) e a metrica "acerto nas respondidas".
- **Dashboard e Relatorio**: desempenho por ano, tipo e assunto, tempo medio por questao, "O que estudar primeiro" e lista das questoes erradas.
- **Importacao de PDF** (extra): envia o PDF de uma prova, o backend extrai as questoes e o gabarito e o usuario escolhe quais salvar; a pagina original fica disponivel no simulado ("Ver pagina do PDF").
- **Assistente de IA** (extra, opcional): explicacao da questao e classificacao por assunto com o Google Gemini. Sem chave configurada, o resto da aplicacao funciona normalmente.

## Tecnologias

| Camada        | Tecnologia                                          |
|---------------|-----------------------------------------------------|
| Backend       | Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Dependencias  | Poetry (backend), npm (frontend)                    |
| Frontend      | React, Vite, Tailwind CSS (JavaScript)              |
| Banco         | PostgreSQL 16                                       |
| Infra         | Docker, Docker Compose, Makefile                    |
| Testes        | Pytest, Vitest + Testing Library, Playwright        |
| Lint/formato  | Ruff (backend), Biome (frontend)                    |
| CI            | GitHub Actions                                      |

## Arquitetura

```
Navegador
   |  http://localhost:3000
   v
frontend (React compilado, servido pelo nginx)
   |  HTTP + JSON  ->  http://localhost:8000   (CORS com origens explicitas)
   v
backend (FastAPI)
   rotas  ->  servicos  ->  repositorios  ->  models
   (HTTP)     (regras)      (SQLAlchemy)      (tabelas)
   |
   v
db (PostgreSQL 16, volume postgres_data, esquema versionado pelo Alembic)
```

- **Rotas** (`app/api/routes`): recebem a requisicao, validam o corpo com os **schemas** Pydantic e convertem erros em codigos HTTP (404, 409, 422, 503).
- **Servicos** (`app/services`): regras de negocio (validacoes, correcao do simulado, modos de sorteio). Nao conhecem HTTP nem SQL.
- **Repositorios** (`app/repositories`): consultas e gravacoes com SQLAlchemy.
- **Models** (`app/models`): tabelas `questoes`, `simulados`, `respostas` e `ciclo_cobertura`.
- **Frontend**: paginas em `src/pages`, componentes em `src/components` e toda a comunicacao HTTP em `src/services/api.js`, com estados de carregamento, sucesso e erro.

## Estrutura do projeto

```
.
├── backend/
│   ├── app/
│   │   ├── api/routes/        # Rotas REST: health, questoes, simulados
│   │   ├── core/              # config.py (variaveis de ambiente) e erros.py (erros 500 com CORS)
│   │   ├── database/          # Engine, sessao e base ORM
│   │   ├── models/            # Questao, Simulado, Resposta, CicloCobertura
│   │   ├── repositories/      # Acesso ao banco (SQLAlchemy)
│   │   ├── schemas/           # Schemas Pydantic (validacao e respostas)
│   │   ├── services/          # Regras de negocio, importacao de PDF e assistente de IA
│   │   ├── tools/             # Ferramentas de linha de comando (PDF, duplicadas)
│   │   ├── seed.py            # Questoes do ENADE 2014 e 2019
│   │   ├── seed_2023.py       # Questoes do ENADE 2023
│   │   └── main.py            # Aplicacao FastAPI, CORS e tratamento de erros
│   ├── alembic/versions/      # 7 migracoes versionadas
│   ├── tests/
│   │   ├── unit/              # Regras de negocio e funcoes puras
│   │   └── integration/       # Endpoints (TestClient)
│   ├── Dockerfile
│   ├── pyproject.toml         # Dependencias (Poetry), Pytest e Ruff
│   └── poetry.lock
├── frontend/
│   ├── src/
│   │   ├── components/        # Navbar, QuestaoForm, QuizQuestao, AjudasQuiz, SoundToggle
│   │   ├── pages/             # Dashboard, Questoes, ImportarPdf, NovoSimulado, Simulado, Historico, Relatorio
│   │   ├── services/api.js    # Camada HTTP (fetch) e mensagens de erro
│   │   ├── sound/             # Efeitos sonoros e musica de fundo
│   │   ├── utils/             # Progresso do simulado e redimensionamento de imagem
│   │   ├── validation.js      # Validacoes dos formularios
│   │   └── App.jsx            # Componente raiz e navegacao
│   ├── tests/                 # Vitest + Testing Library
│   │   └── e2e/               # Playwright (aplicacao real)
│   ├── Dockerfile             # Build com Node e entrega com nginx
│   ├── nginx.conf
│   ├── biome.json
│   └── playwright.config.js
├── .github/workflows/         # backend.yml e frontend.yml (CI)
├── docker-compose.yml         # db + backend + frontend
├── Makefile                   # Comandos de execucao, testes e manutencao
├── .env.example               # Variaveis de ambiente (sem segredos)
└── README.md
```

## Pre-requisitos

- Docker e Docker Compose
- GNU Make (no Windows, use o **Git Bash** ou o WSL para os comandos `make`)
- Node.js 22+ (apenas para rodar os testes do frontend e os testes E2E)

## Variaveis de ambiente

As configuracoes ficam em um arquivo `.env` na raiz, lido pelo Docker Compose. O `.env.example` e o modelo versionado, sem segredos; o `.env` real esta no `.gitignore`.

```bash
make env        # cria o .env a partir do .env.example (nao sobrescreve)
```

| Variavel          | Descricao                                    | Padrao                |
|-------------------|----------------------------------------------|-----------------------|
| POSTGRES_USER     | Usuario do PostgreSQL                        | postgres              |
| POSTGRES_PASSWORD | Senha do PostgreSQL                          | postgres              |
| POSTGRES_DB       | Nome do banco                                | enade_platform        |
| API_PORT          | Porta da API no host                         | 8000                  |
| FRONTEND_PORT     | Porta do frontend no host                    | 3000                  |
| FRONTEND_URL      | Origem do frontend em desenvolvimento (CORS) | http://localhost:5173 |
| VITE_API_URL      | Endereco da API usado pelo frontend          | http://localhost:8000 |
| GEMINI_API_KEY    | Chave do Google Gemini (opcional)            | vazio                 |
| GEMINI_MODEL      | Modelo do Gemini                             | gemini-2.5-flash      |

O CORS aceita apenas as origens `http://localhost:3000` (frontend no Docker) e `http://localhost:5173` (frontend em desenvolvimento) e os metodos GET, POST, PUT, PATCH, DELETE e OPTIONS.

## Como executar

### Inicio rapido

```bash
make setup
```

Esse comando cria o `.env`, sobe os tres containers, aplica as migracoes e popula o banco.

### Passo a passo

```bash
make env          # 1. cria o .env
make up           # 2. sobe db, backend e frontend (docker compose up -d --build)
make ps           # 3. confere se os tres servicos estao de pe
make db-upgrade   # 4. aplica as migracoes (sempre depois do make up)
make seed         # 5. insere 15 questoes do ENADE 2014 e 2019
make seed-2023    # 6. insere 13 questoes do ENADE 2023
```

### Acesso

| O que                 | Endereco                     |
|-----------------------|------------------------------|
| Aplicacao (frontend)  | http://localhost:3000        |
| Documentacao da API   | http://localhost:8000/docs   |
| Verificacao de saude  | http://localhost:8000/health |

Para parar: `make down`. Para parar e apagar o banco: `make down-v`.

### Desenvolvimento local do frontend

```bash
make up              # db + backend no Docker
make front-install   # dependencias do frontend
```

Depois, dentro da pasta `frontend`, o comando `npm run dev` inicia o Vite com recarga automatica em http://localhost:5173.

## Comandos do Makefile

`make help` lista todos os comandos. Cada um e um atalho para um comando `docker compose` ou `npx`.

| Comando                   | O que faz                                                    |
|---------------------------|--------------------------------------------------------------|
| `make setup`              | Prepara tudo do zero (.env, containers, migracoes e seeds)   |
| `make env`                | Cria o `.env` a partir do `.env.example`                     |
| `make up`                 | Sobe os containers (`docker compose up -d --build`)          |
| `make down`               | Para os containers                                           |
| `make down-v`             | Para os containers e remove o volume do banco                |
| `make build`              | Reconstroi as imagens sem cache                              |
| `make restart`            | Reinicia os containers                                       |
| `make ps`                 | Mostra o estado dos containers                               |
| `make logs`               | Mostra os logs em tempo real                                 |
| `make db-upgrade`         | Aplica as migracoes pendentes (`alembic upgrade head`)       |
| `make db-current`         | Mostra a migracao aplicada no banco                          |
| `make db-history`         | Mostra o historico de migracoes                              |
| `make db-downgrade`       | Reverte a ultima migracao                                    |
| `make db-ultimas`         | Mostra as ultimas questoes gravadas no PostgreSQL            |
| `make seed`               | Insere as questoes do ENADE 2014 e 2019                      |
| `make seed-2023`          | Insere as questoes do ENADE 2023 (nao duplica)               |
| `make front-install`      | Instala as dependencias do frontend (`npm ci`)               |
| `make e2e-install`        | Instala o navegador do Playwright                            |
| `make test`               | Roda os testes do backend e do frontend                      |
| `make test-back`          | Testes do backend (Pytest, dentro do container)              |
| `make test-front`         | Testes do frontend (Vitest)                                  |
| `make test-e2e`           | Testes E2E (Playwright) contra a aplicacao em execucao       |
| `make lint`               | Lint e formatacao: Ruff (backend) e Biome (frontend)         |
| `make format`             | Formata o codigo com Ruff e Biome                            |
| `make check-all`          | Lint + testes                                                |
| `make back-sh`            | Abre um shell no container do backend                        |
| `make db-sh`              | Abre o `psql` no banco                                       |
| `make front-sh`           | Abre um shell no container do frontend                       |
| `make duplicadas`         | Lista questoes duplicadas (mesmo ano e numero)               |
| `make remover-duplicadas` | Remove duplicadas que nao estao em nenhum simulado           |
| `make limpar-lixo`        | Remove rodape/codigo de barras de questoes importadas de PDF |
| `make fix-q10-2023`       | Recoloca a imagem da Questao 10 do ENADE 2023                |

## Migracoes

O esquema do banco e versionado com Alembic (`backend/alembic/versions`):

| Ordem | Revisao        | O que faz                                             |
|-------|----------------|-------------------------------------------------------|
| 1     | `56d0baaf5b21` | Cria as tabelas `questoes`, `simulados` e `respostas` |
| 2     | `a1b2c3d4e5f6` | Adiciona dificuldade e tempo de resposta              |
| 3     | `c3d4e5f6a7b8` | Adiciona imagem a questao                             |
| 4     | `d4e5f6a7b8c9` | Cria o ciclo de cobertura (modo "sem repetir")        |
| 5     | `e5f6a7b8c9d0` | Guarda quantas questoes foram respondidas no simulado |
| 6     | `f6a7b8c9d0e1` | Adiciona `fonte` (nome livre da prova)                |
| 7     | `g7b8c9d0e1f2` | Guarda a pagina original do PDF                       |

```bash
make db-upgrade    # aplica todas as migracoes pendentes
make db-current    # deve mostrar g7b8c9d0e1f2 (head)
make db-history    # historico
make db-downgrade  # reverte a ultima
```

## Testes

```bash
make test-back       # 79 testes Pytest (regras de negocio e endpoints)
make front-install   # uma vez, antes dos testes do frontend
make test-front      # 39 testes Vitest + Testing Library (componentes e fluxos)
make lint            # Ruff e Biome
```

Os testes do backend usam um SQLite em memoria (fixtures em `backend/tests/conftest.py`), entao nao alteram o banco do Docker.

### Testes E2E (Playwright)

Os testes E2E exercitam o sistema inteiro (frontend, API e PostgreSQL) e precisam da aplicacao em execucao em http://localhost:3000, com migracoes e seeds aplicados:

```bash
make front-install   # uma vez
make e2e-install     # uma vez: baixa o navegador do Playwright
make test-e2e        # 5 testes
```

O teste `frontend/tests/e2e/persistencia.spec.js` cadastra uma questao pela interface, recarrega a pagina, confere pela API que ela foi gravada, edita, remove e confere novamente. Para apontar para outros enderecos, defina `E2E_BASE_URL` e `E2E_API_URL`.

### Integracao continua

O GitHub Actions roda dois workflows em cada push na `projeto-final` e em cada Pull Request para a `main`:

- **Backend CI** (`.github/workflows/backend.yml`): `ruff check`, `ruff format --check` e `pytest`.
- **Frontend CI** (`.github/workflows/frontend.yml`): `biome check` e `vitest`.

Os testes E2E nao rodam no CI porque dependem dos tres containers em execucao.

## Endpoints da API

A documentacao interativa fica em http://localhost:8000/docs.

### Health

| Metodo | Rota    | Descricao     |
|--------|---------|---------------|
| GET    | /health | Status da API |

### Questoes

| Metodo | Rota                          | Descricao                                                 |
|--------|-------------------------------|-----------------------------------------------------------|
| GET    | /questoes/                    | Lista questoes (filtros: ano, tipo, assunto, dificuldade) |
| POST   | /questoes/                    | Cadastra uma questao                                      |
| GET    | /questoes/{id}                | Busca uma questao                                         |
| PUT    | /questoes/{id}                | Substitui uma questao                                     |
| PATCH  | /questoes/{id}                | Atualiza parcialmente uma questao                         |
| DELETE | /questoes/{id}                | Remove uma questao                                        |
| GET    | /questoes/resumo              | Totais do banco de questoes                               |
| GET    | /questoes/anos                | Anos com questoes cadastradas                             |
| GET    | /questoes/cobertura           | Cobertura do banco no modo "sem repetir"                  |
| POST   | /questoes/cobertura/reiniciar | Inicia um novo ciclo de cobertura                         |
| GET    | /questoes/{id}/estatisticas   | Como a questao ja foi respondida                          |
| POST   | /questoes/importar-pdf        | Extrai questoes de um PDF (nao grava)                     |
| GET    | /questoes/ia/status           | Informa se a IA esta configurada                          |
| POST   | /questoes/classificar-lote    | Classifica questoes por assunto (Gemini)                  |
| POST   | /questoes/{id}/assistente-ia  | Explicacao da questao (Gemini)                            |

### Simulados

| Metodo | Rota                     | Descricao                                           |
|--------|--------------------------|-----------------------------------------------------|
| GET    | /simulados/              | Lista os simulados                                  |
| POST   | /simulados/              | Cria um simulado (aleatorio, sem repetir ou manual) |
| GET    | /simulados/{id}          | Detalhes e respostas de um simulado                 |
| GET    | /simulados/{id}/questoes | Questoes de um simulado                             |
| POST   | /simulados/{id}/submeter | Envia as respostas e corrige                        |
| DELETE | /simulados/{id}          | Remove um simulado                                  |
| GET    | /simulados/dashboard     | Estatisticas de desempenho                          |
| GET    | /simulados/relatorio     | Prioridades de estudo e questoes erradas            |

### Tratamento de erros

| Codigo | Quando acontece                                                  |
|--------|------------------------------------------------------------------|
| 404    | Questao ou simulado inexistente                                  |
| 409    | Simulado ja finalizado                                           |
| 422    | Dados invalidos (validacao dos schemas ou das regras de negocio) |
| 503    | Assistente de IA sem chave configurada                           |
| 500    | Erro inesperado: a resposta traz a causa e mantem os cabecalhos de CORS, para o frontend mostrar a mensagem em vez de "NetworkError" |

O frontend mostra a mensagem devolvida pela API em cada tela.

## Assistente de IA (opcional)

A chave do Gemini fica **somente no backend**, no arquivo `.env`; o navegador nunca a recebe.

1. Crie uma chave gratuita em https://aistudio.google.com/apikey.
2. Cole o valor em `GEMINI_API_KEY=` no arquivo `.env`.
3. Rode `make up` para recriar o backend com a chave.

Sem chave, os endpoints de IA respondem 503 com uma mensagem clara e todo o resto funciona.

## Importacao de PDF (extra)

Na pagina **Questoes**, o botao **Importar PDF** envia a prova ao backend, que extrai o texto e o gabarito com o `pdftotext`. A tela mostra as questoes encontradas e o usuario escolhe quais salvar. Questoes ja cadastradas (mesmo ano e numero) nao sao duplicadas. Provas diagramadas em duas colunas podem vir com o texto misturado; nesses casos a questao e marcada para revisao em vez de ser salva automaticamente.

## Solucao de problemas

- **"relation ... does not exist" na tela**: as migracoes nao foram aplicadas. Rode `make db-upgrade`.
- **Porta em uso (3000, 5432 ou 8000)**: outro projeto Docker Compose esta usando as mesmas portas. Pare-o com `docker compose -p <nome-do-projeto> down` antes de `make up`.
- **`make` nao encontrado no Windows**: use o Git Bash ou o WSL. No PowerShell, os comandos equivalentes estao na coluna "O que faz" da tabela do Makefile (por exemplo, `docker compose up -d --build`).
- **Windows PowerShell 5.1**: o operador `&&` nao existe; rode um comando por linha.
- **Mensagem "Nao foi possivel falar com o servidor"**: confira com `make ps` e `make logs` se o backend esta de pe.

## Video de demonstracao

[Link para o video de demonstracao](https://link-do-video-aqui)

## Autor

**Tiago R. Gregorio** - Engenharia de Computacao, Inatel (2026/2)
