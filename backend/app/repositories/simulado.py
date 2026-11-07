"""Acesso ao banco para os recursos simulado e resposta."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.resposta import Resposta
from app.models.simulado import Simulado


class SimuladoRepository:
    """Unico ponto que conversa com o banco sobre simulados."""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, nome: str, total_questoes: int) -> Simulado:
        simulado = Simulado(nome=nome, total_questoes=total_questoes)
        self.db.add(simulado)
        self.db.commit()
        self.db.refresh(simulado)
        return simulado

    def buscar_por_id(self, simulado_id: int) -> Simulado | None:
        return self.db.get(Simulado, simulado_id)

    def listar(self) -> list[Simulado]:
        consulta = select(Simulado).order_by(Simulado.criado_em.desc())
        return list(self.db.scalars(consulta))

    def adicionar_respostas(
        self, simulado: Simulado, respostas: list[dict]
    ) -> list[Resposta]:
        """Adiciona as respostas e calcula nota do simulado."""
        objetos = []
        for r in respostas:
            resp = Resposta(
                simulado_id=simulado.id,
                questao_id=r["questao_id"],
                alternativa_escolhida=r["alternativa_escolhida"],
                correta=r["correta"],
                tempo_resposta=r.get("tempo_resposta"),
            )
            self.db.add(resp)
            objetos.append(resp)

        acertos = sum(1 for r in respostas if r["correta"])
        simulado.finalizado = True
        simulado.acertos = acertos
        simulado.nota = round((acertos / simulado.total_questoes) * 100, 2)

        self.db.commit()
        for obj in objetos:
            self.db.refresh(obj)
        self.db.refresh(simulado)
        return objetos

    def remover(self, simulado: Simulado) -> None:
        self.db.delete(simulado)
        self.db.commit()

    def contar(self, finalizado: bool | None = None) -> int:
        consulta = select(func.count()).select_from(Simulado)
        if finalizado is not None:
            consulta = consulta.where(Simulado.finalizado == finalizado)
        return self.db.scalar(consulta) or 0

    def media_nota(self) -> float | None:
        """Retorna a media das notas dos simulados finalizados."""
        consulta = (
            select(func.avg(Simulado.nota))
            .where(Simulado.finalizado.is_(True))
        )
        resultado = self.db.scalar(consulta)
        return round(resultado, 2) if resultado is not None else None

    def total_acertos_e_respostas(self) -> tuple[int, int]:
        """Retorna total de acertos e total de respostas."""
        consulta_total = select(func.count()).select_from(Resposta)
        consulta_acertos = (
            select(func.count())
            .select_from(Resposta)
            .where(Resposta.correta.is_(True))
        )
        total = self.db.scalar(consulta_total) or 0
        acertos = self.db.scalar(consulta_acertos) or 0
        return acertos, total

    def desempenho_por_ano(self) -> list[dict]:
        """Agrupa acertos e total de respostas por ano da questao."""
        from app.models.questao import Questao

        consulta = (
            select(
                Questao.ano,
                func.count(Resposta.id).label("total"),
                func.sum(
                    func.cast(Resposta.correta, type_=func.coalesce.type)
                ).label("acertos"),
            )
            .join(Questao, Resposta.questao_id == Questao.id)
            .where(Resposta.correta.is_not(None))
            .group_by(Questao.ano)
            .order_by(Questao.ano)
        )

        resultados = self.db.execute(consulta).all()
        return [
            {
                "ano": r.ano,
                "total": r.total,
                "acertos": int(r.acertos or 0),
                "taxa": round((int(r.acertos or 0) / r.total) * 100, 2)
                if r.total > 0
                else 0,
            }
            for r in resultados
        ]

    def desempenho_por_tipo(self) -> list[dict]:
        """Agrupa acertos e total de respostas por tipo (FG/CE)."""
        from app.models.questao import Questao

        consulta = (
            select(
                Questao.tipo,
                func.count(Resposta.id).label("total"),
                func.sum(
                    func.cast(Resposta.correta, type_=func.coalesce.type)
                ).label("acertos"),
            )
            .join(Questao, Resposta.questao_id == Questao.id)
            .where(Resposta.correta.is_not(None))
            .group_by(Questao.tipo)
            .order_by(Questao.tipo)
        )

        resultados = self.db.execute(consulta).all()
        return [
            {
                "tipo": r.tipo,
                "total": r.total,
                "acertos": int(r.acertos or 0),
                "taxa": round((int(r.acertos or 0) / r.total) * 100, 2)
                if r.total > 0
                else 0,
            }
            for r in resultados
        ]
