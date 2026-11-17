"""Testes de integracao dos endpoints de questoes."""

QUESTAO_VALIDA = {
    "ano": 2019,
    "numero": 9,
    "tipo": "CE",
    "enunciado": "Questao de teste para validacao do endpoint da API REST.",
    "alternativa_a": "Alternativa A do teste",
    "alternativa_b": "Alternativa B do teste",
    "alternativa_c": "Alternativa C do teste",
    "alternativa_d": "Alternativa D do teste",
    "alternativa_e": "Alternativa E do teste",
    "resposta": "C",
    "assunto": "Testes",
    "dificuldade": "facil",
}


class TestCriarQuestao:
    def test_criar_questao_valida(self, client):
        response = client.post("/questoes/", json=QUESTAO_VALIDA)
        assert response.status_code == 201
        data = response.json()
        assert data["ano"] == 2019
        assert data["resposta"] == "C"
        assert "id" in data

    def test_criar_questao_tipo_invalido(self, client):
        dados = {**QUESTAO_VALIDA, "tipo": "XX"}
        response = client.post("/questoes/", json=dados)
        assert response.status_code == 422


class TestListarQuestoes:
    def test_listar_vazio(self, client):
        response = client.get("/questoes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_com_filtro_ano(self, client):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/?ano=2019")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_listar_filtro_ano_sem_resultado(self, client):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/?ano=2014")
        assert response.status_code == 200
        assert len(response.json()) == 0


class TestBuscarQuestao:
    def test_buscar_existente(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.get(f"/questoes/{criada['id']}")
        assert response.status_code == 200

    def test_buscar_inexistente(self, client):
        response = client.get("/questoes/999")
        assert response.status_code == 404


class TestAtualizarQuestao:
    def test_patch_parcial(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.patch(
            f"/questoes/{criada['id']}", json={"dificuldade": "dificil"}
        )
        assert response.status_code == 200
        assert response.json()["dificuldade"] == "dificil"


class TestRemoverQuestao:
    def test_remover_existente(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.delete(f"/questoes/{criada['id']}")
        assert response.status_code == 204

    def test_remover_inexistente(self, client):
        response = client.delete("/questoes/999")
        assert response.status_code == 404


class TestResumoQuestoes:
    def test_resumo_com_dados(self, client):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/resumo")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["componente_especifico"] == 1


class TestImagemQuestao:
    def test_criar_e_atualizar_imagem(self, client):
        dados_com_imagem = {**QUESTAO_VALIDA, "imagem": "data:image/png;base64,abc123"}
        criada = client.post("/questoes/", json=dados_com_imagem).json()
        assert criada["imagem"] == "data:image/png;base64,abc123"

        response = client.patch(
            f"/questoes/{criada['id']}",
            json={"imagem": "data:image/png;base64,outraImagem"},
        )
        assert response.status_code == 200
        assert response.json()["imagem"] == "data:image/png;base64,outraImagem"

    def test_questao_sem_imagem_retorna_null(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        assert criada["imagem"] is None


class TestImportarPdf:
    def test_rejeita_arquivo_que_nao_e_pdf(self, client):
        response = client.post(
            "/questoes/importar-pdf",
            files={"arquivo": ("teste.txt", b"nao sou um pdf", "text/plain")},
            data={"ano": "2019", "inicio_ce": "9"},
        )
        assert response.status_code == 422

    def test_pdf_invalido_retorna_422_em_vez_de_quebrar(self, client):
        response = client.post(
            "/questoes/importar-pdf",
            files={
                "arquivo": (
                    "teste.pdf",
                    b"%PDF-1.4 nao e um pdf valido de verdade",
                    "application/pdf",
                )
            },
            data={"ano": "2019", "inicio_ce": "9"},
        )
        assert response.status_code == 422


class TestStatusIA:
    def test_sem_chave_informa_que_nao_esta_configurada(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.services.assistente_ia.GEMINI_API_KEY", "", raising=False
        )
        data = client.get("/questoes/ia/status").json()
        assert data["configurada"] is False
        assert data["modelo"]
        assert "teste" not in data

    def test_com_chave_mas_sem_testar_nao_chama_o_gemini(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.services.assistente_ia.GEMINI_API_KEY", "chave-falsa", raising=False
        )
        data = client.get("/questoes/ia/status").json()
        assert data["configurada"] is True
        assert "teste" not in data


class TestClassificarLote:
    CORPO = {
        "questoes": [
            {
                "enunciado": "Qual estrutura de dados usa LIFO?",
                "alternativa_a": "Fila",
                "alternativa_b": "Pilha",
                "alternativa_c": "Lista",
                "alternativa_d": "Arvore",
                "alternativa_e": "Grafo",
            }
        ]
    }

    def test_sem_chave_retorna_503_com_mensagem(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.services.assistente_ia.GEMINI_API_KEY", "", raising=False
        )
        response = client.post("/questoes/classificar-lote", json=self.CORPO)
        assert response.status_code == 503
        assert "GEMINI_API_KEY" in response.json()["detail"]

    def test_lista_vazia_retorna_422(self, client):
        response = client.post("/questoes/classificar-lote", json={"questoes": []})
        assert response.status_code == 422


class TestPaginaOriginal:
    def test_guarda_pagina_original_e_nao_vaza_na_listagem(self, client):
        dados = {**QUESTAO_VALIDA, "pagina_original": "data:image/jpeg;base64,abc"}
        criada = client.post("/questoes/", json=dados).json()
        assert "pagina_original" not in criada  # resposta leve

        buscada = client.get(f"/questoes/{criada['id']}").json()
        assert buscada["pagina_original"] == "data:image/jpeg;base64,abc"

        # A listagem e leve: nao carrega a imagem de cada questao.
        item = client.get("/questoes/").json()[0]
        assert "pagina_original" not in item

    def test_anexa_pagina_a_questao_existente_sem_mexer_no_resto(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.patch(
            f"/questoes/{criada['id']}",
            json={"pagina_original": "data:image/jpeg;base64,xyz"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "pagina_original" not in data  # resposta leve
        buscada = client.get(f"/questoes/{criada['id']}").json()
        assert buscada["pagina_original"] == "data:image/jpeg;base64,xyz"
        assert buscada["enunciado"] == criada["enunciado"]
        assert buscada["resposta"] == criada["resposta"]

    def test_listagem_inclui_fonte(self, client):
        dados = {**QUESTAO_VALIDA, "fonte": "Lista de Algoritmos"}
        client.post("/questoes/", json=dados)
        item = client.get("/questoes/").json()[0]
        assert item["fonte"] == "Lista de Algoritmos"


class TestAssistenteIA:
    def test_sem_chave_configurada_retorna_503(self, client):
        """No ambiente de testes nao ha GEMINI_API_KEY configurada, entao o
        endpoint deve falhar de forma previsivel (503), nunca travar."""
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.post(f"/questoes/{criada['id']}/assistente-ia")
        assert response.status_code == 503

    def test_questao_inexistente_retorna_404(self, client):
        response = client.post("/questoes/999/assistente-ia")
        assert response.status_code == 404


class TestCobertura:
    def test_cobertura_vazia(self, client):
        client.post("/questoes/", json=QUESTAO_VALIDA)
        response = client.get("/questoes/cobertura")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["respondidas"] == 0
        assert data["percentual"] == 0.0

    def test_cobertura_apos_responder(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        simulado = client.post(
            "/simulados/", json={"nome": "Cobertura", "quantidade": 1}
        ).json()
        client.post(
            f"/simulados/{simulado['simulado']['id']}/submeter",
            json={
                "respostas": [
                    {"questao_id": criada["id"], "alternativa_escolhida": "A"}
                ]
            },
        )
        response = client.get("/questoes/cobertura")
        data = response.json()
        assert data["respondidas"] == 1
        assert data["percentual"] == 100.0


class TestReiniciarCobertura:
    def test_reiniciar_zera_a_cobertura_sem_apagar_historico(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        simulado = client.post(
            "/simulados/", json={"nome": "Ciclo 1", "quantidade": 1}
        ).json()
        client.post(
            f"/simulados/{simulado['simulado']['id']}/submeter",
            json={
                "respostas": [
                    {"questao_id": criada["id"], "alternativa_escolhida": "C"}
                ]
            },
        )
        assert client.get("/questoes/cobertura").json()["percentual"] == 100.0

        reiniciada = client.post("/questoes/cobertura/reiniciar").json()
        assert reiniciada["percentual"] == 0.0
        assert reiniciada["ciclo"] == 2

        # O historico (listagem de simulados) continua existindo.
        historico = client.get("/simulados/").json()
        assert len(historico) == 1

    def test_modo_sem_repetir_libera_questao_apos_reiniciar(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        primeiro = client.post(
            "/simulados/",
            json={"nome": "Antes", "quantidade": 1, "modo": "sem_repetir"},
        ).json()
        client.post(
            f"/simulados/{primeiro['simulado']['id']}/submeter",
            json={
                "respostas": [
                    {"questao_id": criada["id"], "alternativa_escolhida": "C"}
                ]
            },
        )
        # Sem reiniciar, a unica questao ja foi usada: deve falhar.
        sem_sucesso = client.post(
            "/simulados/",
            json={"nome": "Depois", "quantidade": 1, "modo": "sem_repetir"},
        )
        assert sem_sucesso.status_code == 422

        client.post("/questoes/cobertura/reiniciar")

        # Apos reiniciar, a mesma questao pode ser sorteada de novo.
        depois = client.post(
            "/simulados/",
            json={"nome": "Depois do reinicio", "quantidade": 1, "modo": "sem_repetir"},
        )
        assert depois.status_code == 201
        assert depois.json()["questao_ids"] == [criada["id"]]


class TestFonteQuestao:
    def test_criar_com_fonte_customizada(self, client):
        dados = {**QUESTAO_VALIDA, "fonte": "Lista de Algoritmos - Prof. Fulano"}
        criada = client.post("/questoes/", json=dados).json()
        assert criada["fonte"] == "Lista de Algoritmos - Prof. Fulano"

    def test_questao_sem_fonte_retorna_null(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        assert criada["fonte"] is None


class TestEstatisticasQuestao:
    def test_estatisticas_sem_respostas(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        response = client.get(f"/questoes/{criada['id']}/estatisticas")
        assert response.status_code == 200
        data = response.json()
        assert data["total_respostas"] == 0
        assert data["mais_escolhida"] is None
        assert data["taxa_acerto"] is None

    def test_estatisticas_questao_inexistente(self, client):
        response = client.get("/questoes/999/estatisticas")
        assert response.status_code == 404

    def test_estatisticas_com_respostas(self, client):
        criada = client.post("/questoes/", json=QUESTAO_VALIDA).json()
        questao_id = criada["id"]

        simulado = client.post(
            "/simulados/",
            json={"nome": "Teste Estatisticas", "quantidade": 1},
        ).json()
        simulado_id = simulado["simulado"]["id"]

        client.post(
            f"/simulados/{simulado_id}/submeter",
            json={
                "respostas": [{"questao_id": questao_id, "alternativa_escolhida": "C"}]
            },
        )

        response = client.get(f"/questoes/{questao_id}/estatisticas")
        assert response.status_code == 200
        data = response.json()
        assert data["total_respostas"] == 1
        assert data["por_alternativa"]["C"] == 1
        assert data["mais_escolhida"] == "C"
        assert data["taxa_acerto"] == 100.0
