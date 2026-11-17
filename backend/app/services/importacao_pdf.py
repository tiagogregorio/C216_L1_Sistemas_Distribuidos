"""Processa um PDF enviado pela interface e devolve um rascunho de questoes
para revisao, junto com miniaturas de cada pagina (para o usuario localizar
figuras que precisem ser anexadas manualmente).

Reaproveita a mesma logica de extracao de texto/gabarito do
app/tools/extrair_enade.py (usado via linha de comando); aqui o resultado
e devolvido como dados, para a tela de importacao no frontend, em vez de
um arquivo .py.
"""

import base64
import io
import tempfile
from pathlib import Path

from PIL import Image

from app.tools.extrair_enade import (
    dividir_em_blocos,
    extrair_gabarito,
    extrair_texto,
    rasterizar_paginas,
    separar_enunciado_e_alternativas,
)

LARGURA_MINIATURA = 900  # legivel o bastante para guardar na questao
QUALIDADE_MINIATURA = 68


def _calcular_pagina_de_cada_questao(
    texto: str, blocos: dict[int, str]
) -> dict[int, int]:
    """Estima em qual pagina (1-indexada) cada questao comeca, contando os
    marcadores de quebra de pagina (\\f) do pdftotext antes de cada bloco."""
    paginas = {}
    for numero, bloco in blocos.items():
        posicao = texto.find(bloco)
        if posicao == -1:
            continue
        paginas[numero] = texto.count("\f", 0, posicao) + 1
    return paginas


def _gerar_miniaturas(pasta_paginas: Path) -> list[str]:
    """Converte cada pagina.jpg (JPEG de alta resolucao gerado por
    pdftoppm) em uma miniatura comprimida, como data URI."""
    arquivos = sorted(pasta_paginas.glob("pagina*.jpg"))
    miniaturas = []
    for arquivo in arquivos:
        imagem = Image.open(arquivo).convert("RGB")
        if imagem.width > LARGURA_MINIATURA:
            proporcao = LARGURA_MINIATURA / imagem.width
            imagem = imagem.resize(
                (LARGURA_MINIATURA, int(imagem.height * proporcao)), Image.LANCZOS
            )
        buffer = io.BytesIO()
        imagem.save(buffer, format="JPEG", quality=QUALIDADE_MINIATURA)
        b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        miniaturas.append(f"data:image/jpeg;base64,{b64}")
    return miniaturas


def processar_pdf(conteudo_pdf: bytes, ano: int, inicio_ce: int) -> dict:
    """Extrai questoes candidatas e miniaturas das paginas de um PDF.

    Retorna um dict com "questoes" (rascunhos, nao salvos no banco) e
    "paginas" (miniaturas em base64, uma por pagina do PDF).
    """
    with tempfile.TemporaryDirectory() as pasta_temp:
        pasta = Path(pasta_temp)
        caminho_pdf = pasta / "entrada.pdf"
        caminho_pdf.write_bytes(conteudo_pdf)

        texto = extrair_texto(caminho_pdf)
        gabarito = extrair_gabarito(texto)
        gabarito = {n: letra for n, letra in gabarito.items() if n >= inicio_ce}
        blocos = dividir_em_blocos(texto)
        paginas_por_questao = _calcular_pagina_de_cada_questao(texto, blocos)

        pasta_paginas = pasta / "paginas"
        rasterizar_paginas(caminho_pdf, pasta_paginas)
        miniaturas = _gerar_miniaturas(pasta_paginas)

        # Em paginas de duas colunas o cabecalho de uma questao pode nao ser
        # reconhecido; o texto dela vai parar no bloco da questao anterior.
        ausentes = {n for n in gabarito if n not in blocos}

        questoes = []
        for numero in sorted(gabarito):
            resposta = gabarito[numero]
            bloco = blocos.get(numero, "")
            enunciado, alternativas = separar_enunciado_e_alternativas(bloco)
            questoes.append(
                {
                    "ano": ano,
                    "numero": numero,
                    "tipo": "CE",
                    "enunciado": enunciado,
                    "alternativa_a": alternativas.get("A", ""),
                    "alternativa_b": alternativas.get("B", ""),
                    "alternativa_c": alternativas.get("C", ""),
                    "alternativa_d": alternativas.get("D", ""),
                    "alternativa_e": alternativas.get("E", ""),
                    "resposta": resposta,
                    "assunto": "",
                    "dificuldade": "medio",
                    "pagina": paginas_por_questao.get(numero),
                    "alternativas_incompletas": len(alternativas) < 5,
                    "sem_texto": numero in ausentes,
                    "mistura_possivel": (numero + 1) in ausentes,
                }
            )

        return {"questoes": questoes, "paginas": miniaturas}
