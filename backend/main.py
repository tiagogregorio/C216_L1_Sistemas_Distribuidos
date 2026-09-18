from fastapi import FastAPI

from tarefas import resumir_tarefas

app = FastAPI(title="C216 L1 - Sistemas Distribuidos")

TAREFAS_EM_MEMORIA = [
    {"id": 1, "titulo": "Configurar Docker", "status": "concluida"},
    {"id": 2, "titulo": "Escrever testes", "status": "concluida"},
    {"id": 3, "titulo": "Configurar CI", "status": "pendente"},
    {"id": 4, "titulo": "Abrir o PR", "status": "pendente"},
]


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/tarefas/resumo")
def resumo_das_tarefas():
    return resumir_tarefas(TAREFAS_EM_MEMORIA)
