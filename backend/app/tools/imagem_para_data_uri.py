"""Converte um arquivo de imagem (recortado manualmente de uma pagina) em
uma data URI comprimida, pronta para colar no campo "imagem" de uma
questao no seed.

Depois de rodar app/tools/extrair_enade.py e olhar as paginas geradas em
saida_<ano>/pagina_NN.jpg, recorte a figura que a questao precisa (em
qualquer editor de imagem: Paint, GIMP, Preview, etc.) e salve como um
arquivo .jpg ou .png. Depois rode:

    poetry run python -m app.tools.imagem_para_data_uri caminho/da/imagem.jpg

O resultado e impresso no terminal: copie e cole como o valor do campo
"imagem" da questao correspondente no arquivo de seed.
"""

import base64
import io
import sys
from pathlib import Path

from PIL import Image

LARGURA_MAXIMA = 900
QUALIDADE_JPEG = 82


def gerar_data_uri(caminho_imagem: Path) -> str:
    imagem = Image.open(caminho_imagem).convert("RGB")
    if imagem.width > LARGURA_MAXIMA:
        proporcao = LARGURA_MAXIMA / imagem.width
        nova_altura = int(imagem.height * proporcao)
        imagem = imagem.resize((LARGURA_MAXIMA, nova_altura), Image.LANCZOS)

    buffer = io.BytesIO()
    imagem.save(buffer, format="JPEG", quality=QUALIDADE_JPEG)
    base64_bytes = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{base64_bytes}"


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    caminho = Path(sys.argv[1])
    if not caminho.exists():
        print(f"Arquivo nao encontrado: {caminho}")
        sys.exit(1)

    data_uri = gerar_data_uri(caminho)
    tamanho_kb = len(data_uri) / 1024
    print(f"\n--- data URI ({tamanho_kb:.0f} KB) ---\n")
    print(data_uri)
    print(f"\n--- fim ({tamanho_kb:.0f} KB) ---")


if __name__ == "__main__":
    main()
