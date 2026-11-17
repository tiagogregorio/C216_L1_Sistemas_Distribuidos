"""Lista (e, se pedido, remove) questoes duplicadas: mesmo ano e numero.

    make duplicadas           # so lista
    make remover-duplicadas   # remove as copias mais novas

Regra da remocao: mantem a questao mais antiga (menor id) e remove as outras,
mas SO as que nao estao ligadas a nenhum simulado. Copias que ja aparecem em
simulados sao mantidas e apontadas, para nao apagar historico.
"""

import sys
from collections import defaultdict

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.models.questao import Questao
from app.models.resposta import Resposta


def executar(remover: bool) -> None:
    engine = create_engine(DATABASE_URL)
    with sessionmaker(bind=engine)() as session:
        grupos = defaultdict(list)
        for questao in session.scalars(select(Questao).order_by(Questao.id)):
            grupos[(questao.ano, questao.numero)].append(questao)

        duplicadas = {k: v for k, v in grupos.items() if len(v) > 1}
        if not duplicadas:
            print("Nenhuma questao duplicada (mesmo ano e numero).")
            return

        removidas = 0
        for (ano, numero), questoes in sorted(duplicadas.items()):
            ids = [q.id for q in questoes]
            print(f"ENADE {ano} Q{numero}: ids {ids} (manteria o id {ids[0]})")
            if not remover:
                continue
            for extra in questoes[1:]:
                usos = session.scalar(
                    select(func.count())
                    .select_from(Resposta)
                    .where(Resposta.questao_id == extra.id)
                )
                if usos:
                    print(f"  id {extra.id} mantida: aparece em {usos} simulado(s).")
                    continue
                session.delete(extra)
                removidas += 1
                print(f"  id {extra.id} removida.")

        if remover:
            session.commit()
            print(f"{removidas} duplicada(s) removida(s).")
        else:
            print(
                f"{len(duplicadas)} grupo(s) duplicado(s). "
                "Rode 'make remover-duplicadas' para limpar."
            )


if __name__ == "__main__":
    executar(remover="--remover" in sys.argv)
