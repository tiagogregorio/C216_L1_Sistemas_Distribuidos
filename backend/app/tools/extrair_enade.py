"""Extrai questoes objetivas de uma prova do ENADE (ou similar) em PDF.

O QUE ESTE SCRIPT AUTOMATIZA:
  - Le o texto do PDF e localiza o gabarito oficial no final do arquivo.
  - Separa o texto em blocos por "QUESTAO N" e tenta identificar o
    enunciado e as 5 alternativas (A a E) de cada questao objetiva.
  - Rasteriza cada pagina do PDF como imagem JPEG, para revisao visual.
  - Gera um arquivo Python de seed (rascunho) com tudo que conseguiu
    extrair, pronto para revisar e rodar.

O QUE CONTINUA MANUAL (de proposito):
  - Decidir quais questoes precisam de uma imagem (grafico, circuito,
    codigo, tabela como figura) — isso exige julgamento humano sobre
    o que e essencial para responder a questao.
  - Recortar a imagem certa de cada pagina e anexar na questao.
  - Revisar o texto extraido: PDFs com fontes corrompidas (alguns anos
    do ENADE tem esse problema) produzem texto ilegivel; nesses casos
    o script avisa, mas a transcricao correta precisa ser manual.
  - Conferir questoes vizinhas a um aviso "nao encontrada": quando duas
    questoes ficam lado a lado na mesma pagina (layout em colunas), a
    extracao pode nao reconhecer uma delas e misturar seu conteudo com
    a questao anterior. O relatorio aponta a questao que sumiu, mas o
    efeito colateral (contaminacao) pode aparecer na vizinha — sempre
    confira o enunciado gerado contra a pagina renderizada antes de
    usar, mesmo nas questoes sem aviso.

COMO USAR:
    cd backend
    poetry run python -m app.tools.extrair_enade <caminho_do_pdf> <ano> \\
        --inicio-ce <numero_da_primeira_questao_do_componente_especifico>

    Exemplo (a prova tem 9 questoes de Formacao Geral objetivas antes do
    Componente Especifico comecar na questao 9):
    poetry run python -m app.tools.extrair_enade \\
        /mnt/user-data/uploads/engenharia-computacao-2019.pdf 2019 \\
        --inicio-ce 9

IMPORTANTE: o gabarito do ENADE junta, na mesma tabela, as questoes de
Formacao Geral (comuns a todos os cursos: atualidades, redacao de
problemas, etc.) e as do Componente Especifico (da area do curso). Este
script so extrai as questoes do Componente Especifico, a partir do
numero informado em --inicio-ce; descubra esse numero folheando as
primeiras paginas do PDF (geralmente logo apos "QUESTAO DISCURSIVA 02"
ou a ultima questao de Formacao Geral). Sem --inicio-ce, o script avisa
e extrai a partir da questao 1 — revise com atencao, pois questoes de
Formacao Geral vao aparecer marcadas como se fossem da area.

Gera em app/tools/saida_<ano>/:
  - rascunho_<ano>.py      -> lista de questoes em formato Python, pronta
                              para revisar e copiar para um seed_<ano>.py
  - pagina_NN.jpg          -> cada pagina do PDF, para localizar e
                              recortar imagens manualmente
  - RELATORIO.txt          -> quais questoes extrairam bem, quais tem
                              poucas alternativas (revisar) e quais nao
                              foram encontradas no gabarito
"""

import re
import subprocess
import sys
from pathlib import Path

PADRAO_QUESTAO = re.compile(r"^QUESTÃO\s+(\d+)\s*$", re.MULTILINE)
PADRAO_GABARITO_ITEM = re.compile(r"QUESTÃO\s+(\d+)\s+(ANULADA|[A-E])\b", re.MULTILINE)
PADRAO_ALTERNATIVA = re.compile(
    r"^([A-E])\s+(.+?)(?=^[A-E]\s|\Z)", re.MULTILINE | re.DOTALL
)
# Lixo de layout que o pdftotext cola no texto das questoes.
PADRAO_LIXO_VALIDINEP = re.compile(r"\s*VALIDI\S*")  # VALIDINEP2023VALIDINEP2023...
PADRAO_CODIGO_BARRAS = re.compile(r"\s*\*R\d{5,}\*")  # *R08202319*
_CURSO_RODAPE = (
    r"(?:Engenharia|ENGENHARIA)(?:\s+MAT[ÉE]RIA)?"
    r"\s+(?:de|DE)\s+(?:Computa[çc][ãa]o|COMPUTA[ÇC][ÃA]O)"
)
# Rodape de pagina no MEIO do texto: so remove se houver numero de pagina colado.
PADRAO_RODAPE_NO_MEIO = re.compile(
    r"\s*(?:\b\d{1,3}\s+" + _CURSO_RODAPE + r"|" + _CURSO_RODAPE + r"\s+\d{1,3}\b)"
)
# Rodape no FIM da ultima alternativa (E): corta dali ate o final do texto.
PADRAO_RODAPE_NO_FIM = re.compile(
    r"(?:\s+\d{1,3})?\s+(?:"
    + _CURSO_RODAPE
    + r"|[ÁA]rea\s+livre|[ÁA]REA\s+LIVRE|\*R\d{5,}\*).*$"
)


def limpar_texto_extraido(texto: str, ultima_alternativa: bool = False) -> str:
    """Remove marcas de validacao, codigo de barras e rodape de pagina.

    Na ultima alternativa (E) o rodape da pagina costuma vir colado ao fim
    do texto, entao ele e cortado dali ate o final.
    """
    texto = " ".join(texto.split())
    texto = PADRAO_LIXO_VALIDINEP.sub("", texto)
    if ultima_alternativa:
        texto = PADRAO_RODAPE_NO_FIM.sub("", texto)
    texto = PADRAO_CODIGO_BARRAS.sub("", texto)
    texto = PADRAO_RODAPE_NO_MEIO.sub("", texto)
    return texto.strip()


def extrair_texto(caminho_pdf: Path) -> str:
    """Usa pdftotext (poppler-utils) para extrair o texto em camadas."""
    resultado = subprocess.run(
        ["pdftotext", "-layout", str(caminho_pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return resultado.stdout


def extrair_gabarito(texto: str) -> dict[int, str]:
    """Extrai o mapa {numero_da_questao: letra_correta} do gabarito oficial."""
    gabarito = {}
    for numero_str, letra in PADRAO_GABARITO_ITEM.findall(texto):
        if letra == "ANULADA":
            continue
        gabarito[int(numero_str)] = letra
    return gabarito


def dividir_em_blocos(texto: str) -> dict[int, str]:
    """Divide o texto em um bloco por numero de questao objetiva."""
    marcas = list(PADRAO_QUESTAO.finditer(texto))
    blocos = {}
    for i, marca in enumerate(marcas):
        numero = int(marca.group(1))
        inicio = marca.end()
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        blocos[numero] = texto[inicio:fim].strip()
    return blocos


def separar_enunciado_e_alternativas(bloco: str) -> tuple[str, dict[str, str]]:
    """Tenta separar o enunciado das 5 alternativas (A-E) de um bloco."""
    alternativas = {}
    for letra, corpo in PADRAO_ALTERNATIVA.findall(bloco):
        alternativas[letra] = limpar_texto_extraido(
            corpo, ultima_alternativa=(letra == "E")
        )

    if alternativas:
        primeira_letra = min(
            alternativas, key=lambda letra_: bloco.find(f"\n{letra_} ")
        )
        pos_corte = bloco.find(f"\n{primeira_letra} ")
        enunciado = bloco[:pos_corte] if pos_corte > 0 else bloco
    else:
        enunciado = bloco

    return limpar_texto_extraido(enunciado), alternativas


def rasterizar_paginas(caminho_pdf: Path, pasta_saida: Path) -> int:
    """Gera um JPEG por pagina do PDF, para revisao visual manual."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    prefixo = pasta_saida / "pagina"
    subprocess.run(
        ["pdftoppm", "-jpeg", "-r", "150", str(caminho_pdf), str(prefixo)],
        check=True,
    )
    return len(list(pasta_saida.glob("pagina*.jpg")))


def gerar_rascunho(
    ano: int,
    tipo: str,
    gabarito: dict[int, str],
    blocos: dict[int, str],
) -> tuple[str, list[str]]:
    """Monta o arquivo .py de rascunho e a lista de avisos para o relatorio."""
    linhas = [
        '"""Rascunho gerado por app.tools.extrair_enade — REVISE ANTES DE USAR.',
        "",
        "Confira cada enunciado e alternativa contra o PDF original, decida",
        "quais questoes precisam de imagem (ver pagina_NN.jpg) e so entao",
        "copie este conteudo para um seed_<ano>.py de verdade, seguindo o",
        "padrao de app/seed_2023.py (script idempotente, verifica ano+numero",
        "antes de inserir).",
        '"""',
        "",
        f"QUESTOES_{ano}_RASCUNHO = [",
    ]
    avisos = []

    for numero in sorted(gabarito):
        resposta = gabarito[numero]
        bloco = blocos.get(numero)
        if bloco is None:
            avisos.append(
                f"Questao {numero}: esta no gabarito mas nao foi encontrada "
                "no texto (pagina pode ter layout incomum). Revisar manualmente."
            )
            continue

        enunciado, alternativas = separar_enunciado_e_alternativas(bloco)
        if len(alternativas) < 5:
            avisos.append(
                f"Questao {numero}: so {len(alternativas)}/5 alternativas "
                "identificadas automaticamente. Provavelmente tem tabela, "
                "grafico ou codigo quebrando o layout do texto — revisar "
                f"contra pagina_NN.jpg e o enunciado abaixo manualmente."
            )

        linhas.append("    {")
        linhas.append(f'        "ano": {ano},')
        linhas.append(f'        "numero": {numero},')
        linhas.append(f'        "tipo": "{tipo}",')
        linhas.append(f"        'enunciado': {enunciado!r},")
        for letra in "ABCDE":
            chave = f"alternativa_{letra.lower()}"
            valor = alternativas.get(letra, "REVISAR_MANUALMENTE")
            linhas.append(f"        '{chave}': {valor!r},")
        linhas.append(f'        "resposta": "{resposta}",')
        linhas.append('        "assunto": "REVISAR",')
        linhas.append('        "dificuldade": "medio",')
        linhas.append('        # "imagem": None,  # preencher se a questao precisar')
        linhas.append("    },")

    linhas.append("]")
    return "\n".join(linhas), avisos


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    caminho_pdf = Path(sys.argv[1])
    ano = int(sys.argv[2])
    tipo = "CE"

    inicio_ce = 1
    if "--inicio-ce" in sys.argv:
        idx = sys.argv.index("--inicio-ce")
        inicio_ce = int(sys.argv[idx + 1])
    else:
        print(
            "AVISO: --inicio-ce nao informado. O gabarito do ENADE mistura "
            "questoes de Formacao Geral com as do Componente Especifico; "
            "sem indicar onde o Componente Especifico comeca, TODAS as "
            "questoes do gabarito serao extraidas e marcadas como CE — "
            "revise e remova as de Formacao Geral do rascunho."
        )

    if not caminho_pdf.exists():
        print(f"Arquivo nao encontrado: {caminho_pdf}")
        sys.exit(1)

    pasta_saida = Path(__file__).parent / f"saida_{ano}"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    print(f"Lendo {caminho_pdf}...")
    texto = extrair_texto(caminho_pdf)

    print("Extraindo gabarito...")
    gabarito = extrair_gabarito(texto)
    if not gabarito:
        print(
            "AVISO: nenhum gabarito encontrado. O PDF pode ter fonte "
            "corrompida (comum em alguns anos do ENADE) ou um layout "
            "diferente do esperado. Revise o texto extraido manualmente."
        )

    print(f"Gabarito: {len(gabarito)} questoes encontradas no total.")
    gabarito = {n: letra for n, letra in gabarito.items() if n >= inicio_ce}
    print(
        f"Mantendo {len(gabarito)} questoes a partir do numero {inicio_ce} "
        "(Componente Especifico)."
    )

    print("Dividindo questoes...")
    blocos = dividir_em_blocos(texto)

    print("Rasterizando paginas para revisao visual...")
    total_paginas = rasterizar_paginas(caminho_pdf, pasta_saida)
    print(f"{total_paginas} paginas salvas em {pasta_saida}/pagina_NN.jpg")

    rascunho, avisos = gerar_rascunho(ano, tipo, gabarito, blocos)

    caminho_rascunho = pasta_saida / f"rascunho_{ano}.py"
    caminho_rascunho.write_text(rascunho, encoding="utf-8")

    caminho_relatorio = pasta_saida / "RELATORIO.txt"
    linhas_relatorio = [
        f"Extracao da prova de {ano} ({tipo})",
        f"Inicio do Componente Especifico considerado: questao {inicio_ce}",
        f"Questoes no gabarito (a partir de {inicio_ce}): {len(gabarito)}",
        f"Questoes com bloco de texto encontrado: {len(blocos)}",
        "",
        "AVISOS (revisar manualmente):",
    ]
    linhas_relatorio.extend(f"  - {aviso}" for aviso in avisos) or (
        linhas_relatorio.append("  (nenhum — mas revise mesmo assim!)")
    )
    caminho_relatorio.write_text("\n".join(linhas_relatorio), encoding="utf-8")

    print(f"\nRascunho salvo em: {caminho_rascunho}")
    print(f"Relatorio salvo em: {caminho_relatorio}")
    print(f"{len(avisos)} questoes precisam de atencao extra (ver RELATORIO.txt).")


if __name__ == "__main__":
    main()
