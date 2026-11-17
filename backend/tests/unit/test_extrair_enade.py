"""Testes da limpeza de texto extraido de PDF (rodape, codigo de barras...)."""

from app.tools.extrair_enade import (
    limpar_texto_extraido,
    separar_enunciado_e_alternativas,
)


def test_remove_marcas_validinep():
    texto = "Texto VALIDINEP2023VALIDINEP2023VALIDIN3P2023 fim"
    assert limpar_texto_extraido(texto) == "Texto fim"


def test_ultima_alternativa_perde_rodape_com_numero_antes():
    texto = "[2, 4, 6, 8, 7, 5, 3, 1]. 18 Engenharia de Computação *R08202319*"
    resultado = limpar_texto_extraido(texto, ultima_alternativa=True)
    assert resultado == "[2, 4, 6, 8, 7, 5, 3, 1]."


def test_ultima_alternativa_perde_rodape_embaralhado():
    texto = (
        "As asserções I e II são proposições falsas. "
        "Engenharia MATÉRIA de Computação 3 *4* *R0820234* LOGO"
    )
    resultado = limpar_texto_extraido(texto, ultima_alternativa=True)
    assert resultado == "As asserções I e II são proposições falsas."


def test_ultima_alternativa_perde_area_livre():
    texto = "I, II e III. Área livre ENGENHARIA DE COMPUTAÇÃO 17 *R09201918*"
    assert limpar_texto_extraido(texto, ultima_alternativa=True) == "I, II e III."


def test_texto_legitimo_nao_e_alterado():
    texto = "A disciplina de Engenharia de Software trata de processos."
    assert limpar_texto_extraido(texto, ultima_alternativa=True) == texto


def test_separacao_limpa_rodape_so_na_alternativa_e():
    bloco = (
        "Qual estrutura usa LIFO?\nA Fila\nB Pilha\nC Lista\nD Arvore\n"
        "E Grafo 7 Engenharia de Computação *R0820237*"
    )
    enunciado, alternativas = separar_enunciado_e_alternativas(bloco)
    assert enunciado == "Qual estrutura usa LIFO?"
    assert alternativas["B"] == "Pilha"
    assert alternativas["E"] == "Grafo"
