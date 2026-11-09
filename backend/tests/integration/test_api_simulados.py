"""Testes de integracao dos endpoints de simulados."""

QUESTAO = {
    "ano": 2019,
    "numero": 1,
    "tipo": "CE",
    "enunciado": "Questao de teste para simulado completo da plataforma.",
    "alternativa_a": "Opcao A",
    "alternativa_b": "Opcao B",
    "alternativa_c": "Opcao C",
    "alternativa_d": "Opcao D",
    "alternativa_e": "Opcao E",
    "resposta": "A",
    "dificuldade": "facil",
}


def criar_questoes(client, n=5):
    ids = []
    for i in range(n):
        q = {**QUESTAO, "numero": i + 1}
        resp = client.post("/questoes/", json=q)
        ids.append(resp.json()["id"])
    return ids


class TestCriarSimulado:
    def test_criar_simulado_com_questoes(self, client):
        criar_questoes(client, 5)
        response = client.post(
            "/simulados/",
            json={"nome": "Teste Simulado", "quantidade": 3},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["simulado"]["nome"] == "Teste Simulado"
        assert len(data["questao_ids"]) == 3

    def test_criar_simulado_questoes_insuficientes(self, client):
        criar_questoes(client, 2)
        response = client.post(
            "/simulados/",
            json={"nome": "Teste Sem Questoes", "quantidade": 10},
        )
        assert response.status_code == 422


class TestModoSemRepetir:
    def test_nao_sorteia_questao_ja_respondida(self, client):
        questao_ids = criar_questoes(client, 3)

        primeiro = client.post(
            "/simulados/",
            json={"nome": "Primeiro", "quantidade": 1, "modo": "sem_repetir"},
        ).json()
        respondida_id = primeiro["questao_ids"][0]
        client.post(
            f"/simulados/{primeiro['simulado']['id']}/submeter",
            json={
                "respostas": [
                    {"questao_id": respondida_id, "alternativa_escolhida": "A"}
                ]
            },
        )

        # Pede as outras duas que restam, sem repetir a primeira.
        segundo = client.post(
            "/simulados/",
            json={"nome": "Segundo", "quantidade": 2, "modo": "sem_repetir"},
        ).json()
        assert respondida_id not in segundo["questao_ids"]
        assert set(segundo["questao_ids"]).issubset(set(questao_ids))

    def test_erro_quando_esgotou_as_questoes_sem_repetir(self, client):
        criar_questoes(client, 2)
        primeiro = client.post(
            "/simulados/",
            json={"nome": "Esgota", "quantidade": 2, "modo": "sem_repetir"},
        ).json()
        respostas = [
            {"questao_id": qid, "alternativa_escolhida": "A"}
            for qid in primeiro["questao_ids"]
        ]
        client.post(
            f"/simulados/{primeiro['simulado']['id']}/submeter",
            json={"respostas": respostas},
        )

        response = client.post(
            "/simulados/",
            json={"nome": "Sem mais", "quantidade": 1, "modo": "sem_repetir"},
        )
        assert response.status_code == 422


class TestQuestoesDoSimulado:
    def test_retoma_simulado_antes_de_submeter(self, client):
        """As questoes devem estar disponiveis mesmo sem nenhuma resposta
        enviada ainda, para permitir retomar um simulado em andamento."""
        questao_ids = criar_questoes(client, 3)
        criado = client.post(
            "/simulados/",
            json={"nome": "Retomar Depois", "quantidade": 3},
        ).json()
        simulado_id = criado["simulado"]["id"]

        response = client.get(f"/simulados/{simulado_id}/questoes")
        assert response.status_code == 200
        ids_retornados = {q["id"] for q in response.json()}
        assert ids_retornados == set(criado["questao_ids"])
        assert ids_retornados.issubset(set(questao_ids))


class TestSubmeterRespostas:
    def test_submeter_e_corrigir(self, client):
        criar_questoes(client, 3)
        criado = client.post(
            "/simulados/",
            json={"nome": "Simulado Correcao", "quantidade": 3},
        ).json()

        simulado_id = criado["simulado"]["id"]
        questao_ids = criado["questao_ids"]

        respostas = [
            {"questao_id": qid, "alternativa_escolhida": "A"} for qid in questao_ids
        ]

        response = client.post(
            f"/simulados/{simulado_id}/submeter",
            json={"respostas": respostas},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["finalizado"] is True
        assert data["nota"] is not None

    def test_submeter_simulado_ja_finalizado(self, client):
        criar_questoes(client, 2)
        criado = client.post(
            "/simulados/",
            json={"nome": "Ja Finalizado", "quantidade": 2},
        ).json()

        simulado_id = criado["simulado"]["id"]
        questao_ids = criado["questao_ids"]

        respostas = [
            {"questao_id": qid, "alternativa_escolhida": "A"} for qid in questao_ids
        ]
        client.post(
            f"/simulados/{simulado_id}/submeter",
            json={"respostas": respostas},
        )

        response = client.post(
            f"/simulados/{simulado_id}/submeter",
            json={"respostas": respostas},
        )
        assert response.status_code == 409


class TestDashboard:
    def test_dashboard_vazio(self, client):
        response = client.get("/simulados/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_simulados"] == 0

    def test_dashboard_com_dados(self, client):
        criar_questoes(client, 3)
        criado = client.post(
            "/simulados/",
            json={"nome": "Dashboard Test", "quantidade": 3},
        ).json()

        respostas = [
            {"questao_id": qid, "alternativa_escolhida": "A"}
            for qid in criado["questao_ids"]
        ]
        client.post(
            f"/simulados/{criado['simulado']['id']}/submeter",
            json={"respostas": respostas},
        )

        response = client.get("/simulados/dashboard")
        data = response.json()
        assert data["simulados_finalizados"] == 1
        assert data["media_nota"] is not None


class TestDesempenhoPorAssunto:
    def test_dashboard_agrupa_por_assunto(self, client):
        questao = {**QUESTAO, "assunto": "Redes de Computadores"}
        resp = client.post("/questoes/", json=questao)
        questao_id = resp.json()["id"]

        criado = client.post(
            "/simulados/",
            json={"nome": "Teste Assunto", "quantidade": 1},
        ).json()
        client.post(
            f"/simulados/{criado['simulado']['id']}/submeter",
            json={
                "respostas": [{"questao_id": questao_id, "alternativa_escolhida": "A"}]
            },
        )

        response = client.get("/simulados/dashboard")
        data = response.json()
        assuntos = {item["assunto"]: item for item in data["desempenho_por_assunto"]}
        assert "Redes de Computadores" in assuntos
        assert assuntos["Redes de Computadores"]["total"] == 1
        assert assuntos["Redes de Computadores"]["acertos"] == 1


class TestRelatorio:
    def test_relatorio_lista_questoes_erradas_e_prioridades(self, client):
        certa = client.post("/questoes/", json=QUESTAO).json()
        errada = client.post(
            "/questoes/",
            json={**QUESTAO, "numero": 2, "assunto": "Grafos"},
        ).json()

        criado = client.post(
            "/simulados/", json={"nome": "Relatorio", "quantidade": 2}
        ).json()
        client.post(
            f"/simulados/{criado['simulado']['id']}/submeter",
            json={
                "respostas": [
                    {"questao_id": certa["id"], "alternativa_escolhida": "A"},
                    {"questao_id": errada["id"], "alternativa_escolhida": "B"},
                ]
            },
        )

        response = client.get("/simulados/relatorio")
        assert response.status_code == 200
        data = response.json()
        assert "questoes_erradas" in data
        assert "prioridades_de_estudo" in data
        ids_errados = {q["questao_id"] for q in data["questoes_erradas"]}
        assert errada["id"] in ids_errados
        assert certa["id"] not in ids_errados


class TestRemoverSimulado:
    def test_remover_existente(self, client):
        criar_questoes(client, 2)
        criado = client.post(
            "/simulados/",
            json={"nome": "Para Remover", "quantidade": 2},
        ).json()
        response = client.delete(f"/simulados/{criado['simulado']['id']}")
        assert response.status_code == 204
