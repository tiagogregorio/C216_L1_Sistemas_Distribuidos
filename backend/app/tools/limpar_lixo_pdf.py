"""Remove lixo de extracao de PDF das questoes JA salvas no banco.

Tira marcas "VALIDINEP...", codigos de barras (*R08202319*) e rodape de
pagina ("18 Engenharia de Computacao") que ficaram no enunciado e nas
alternativas. Seguro para rodar varias vezes: so altera o que tem lixo.

    make limpar-lixo
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.models.questao import Questao
from app.tools.extrair_enade import limpar_texto_extraido


def executar() -> None:
    engine = create_engine(DATABASE_URL)
    with sessionmaker(bind=engine)() as session:
        atualizadas = 0
        for questao in session.query(Questao).all():
            mudou = False

            novo = limpar_texto_extraido(questao.enunciado)
            if novo and novo != questao.enunciado:
                questao.enunciado = novo
                mudou = True

            for letra in "abcde":
                campo = f"alternativa_{letra}"
                atual = getattr(questao, campo)
                novo = limpar_texto_extraido(atual, ultima_alternativa=(letra == "e"))
                if novo and novo != atual:
                    setattr(questao, campo, novo)
                    mudou = True

            if mudou:
                atualizadas += 1
                print(f"Limpa: ENADE {questao.ano} Q{questao.numero} (id {questao.id})")

        session.commit()
    print(f"{atualizadas} questao(oes) limpa(s).")


if __name__ == "__main__":
    executar()
