from fastapi import status


def test_rota_raiz_responde_status_ok(client):
    resposta = client.get("/")

    assert resposta.status_code == status.HTTP_200_OK
    assert resposta.json() == {"status": "ok"}


def test_rota_de_resumo_retorna_o_agregado_das_tarefas(client):
    resposta = client.get("/tarefas/resumo")
    corpo = resposta.json()

    assert resposta.status_code == status.HTTP_200_OK
    assert corpo["total"] == 4
    assert corpo["concluidas"] == 2
    assert corpo["progresso"] == 50.0


def test_rota_inexistente_retorna_not_found(client):
    resposta = client.get("/rota-que-nao-existe")

    assert resposta.status_code == status.HTTP_404_NOT_FOUND
