from fastapi import status


def test_health_check_responde_ok(client):
    resposta = client.get("/")

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == {"status": "ok"}


def test_listar_sem_tarefas_retorna_lista_vazia(client):
    resposta = client.get("/tarefas")

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == []


def test_criar_tarefa_retorna_201(client):
    resposta = client.post(
        "/tarefas",
        json={"titulo": "Escrever testes", "prioridade": "alta"},
    )
    corpo = resposta.json()

    assert resposta.status_code == status.HTTP_201_CREATED
    assert corpo["id"] == 1
    assert corpo["titulo"] == "Escrever testes"
    assert corpo["status"] == "pendente"


def test_criar_tarefa_com_titulo_curto_retorna_422(client):
    resposta = client.post("/tarefas", json={"titulo": "ab"})

    assert resposta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_criar_tarefa_com_prioridade_invalida_retorna_422(client):
    resposta = client.post(
        "/tarefas",
        json={"titulo": "Tarefa valida", "prioridade": "urgentissima"},
    )

    assert resposta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_buscar_tarefa_por_id(client, tarefa_criada):
    resposta = client.get(f"/tarefas/{tarefa_criada['id']}")

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == tarefa_criada


def test_buscar_tarefa_inexistente_retorna_404(client):
    resposta = client.get("/tarefas/999")

    assert resposta.status_code == status.HTTP_404_NOT_FOUND
    assert "999" in resposta.json()["detail"]


def test_listar_com_filtro_de_status(client):
    client.post("/tarefas", json={"titulo": "Tarefa pendente"})
    client.post(
        "/tarefas",
        json={"titulo": "Tarefa pronta", "status": "concluida"},
    )

    resposta = client.get("/tarefas", params={"status": "concluida"})
    corpo = resposta.json()

    assert resposta.status_code == status.HTTP_200_OK
    assert len(corpo) == 1
    assert corpo[0]["titulo"] == "Tarefa pronta"


def test_substituir_tarefa_com_put(client, tarefa_criada):
    resposta = client.put(
        f"/tarefas/{tarefa_criada['id']}",
        json={"titulo": "Titulo substituido"},
    )
    corpo = resposta.json()

    assert resposta.status_code == status.HTTP_200_OK
    assert corpo["titulo"] == "Titulo substituido"
    assert corpo["prioridade"] == "media"


def test_substituir_tarefa_inexistente_retorna_404(client):
    resposta = client.put("/tarefas/999", json={"titulo": "Nao existe"})

    assert resposta.status_code == status.HTTP_404_NOT_FOUND


def test_atualizar_parcialmente_com_patch(client, tarefa_criada):
    resposta = client.patch(
        f"/tarefas/{tarefa_criada['id']}",
        json={"status": "concluida"},
    )
    corpo = resposta.json()

    assert resposta.status_code == status.HTTP_200_OK
    assert corpo["status"] == "concluida"
    assert corpo["titulo"] == tarefa_criada["titulo"]
    assert corpo["prioridade"] == tarefa_criada["prioridade"]


def test_atualizar_tarefa_inexistente_retorna_404(client):
    resposta = client.patch("/tarefas/999", json={"status": "concluida"})

    assert resposta.status_code == status.HTTP_404_NOT_FOUND


def test_remover_tarefa_retorna_204(client, tarefa_criada):
    resposta = client.delete(f"/tarefas/{tarefa_criada['id']}")

    assert resposta.status_code == status.HTTP_204_NO_CONTENT
    assert client.get("/tarefas").json() == []


def test_remover_tarefa_inexistente_retorna_404(client):
    resposta = client.delete("/tarefas/999")

    assert resposta.status_code == status.HTTP_404_NOT_FOUND


def test_resumo_reflete_as_tarefas_cadastradas(client):
    client.post("/tarefas", json={"titulo": "Tarefa pendente"})
    client.post(
        "/tarefas",
        json={"titulo": "Tarefa pronta", "status": "concluida"},
    )

    corpo = client.get("/tarefas/resumo").json()

    assert corpo["total"] == 2
    assert corpo["concluidas"] == 1
    assert corpo["progresso"] == 50.0
