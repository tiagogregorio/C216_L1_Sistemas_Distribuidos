"""Regras de negocio das questoes. Nao conhece HTTP nem SQL."""

from app.models.questao import Questao
from app.repositories.questao import QuestaoRepository
from app.schemas.questao import QuestaoCreate, QuestaoUpdate


class QuestaoNaoEncontradaError(Exception):
    """Levantada quando o identificador informado nao existe."""


def normalizar_enunciado(enunciado: str) -> str:
    """Remove espacos duplicados do enunciado."""
    limpo = " ".join(enunciado.split())
    if not limpo:
        raise ValueError("O enunciado nao pode ser vazio.")
    return limpo


def validar_tipo(tipo: str) -> str:
    """Garante que o tipo seja FG ou CE."""
    valor = tipo.strip().upper()
    if valor not in ("FG", "CE"):
        raise ValueError(f"Tipo invalido: {tipo}. Use FG ou CE.")
    return valor


def validar_resposta(resposta: str) -> str:
    """Garante que a resposta seja uma letra de A a E."""
    valor = resposta.strip().upper()
    if valor not in ("A", "B", "C", "D", "E"):
        raise ValueError(f"Resposta invalida: {resposta}. Use A, B, C, D ou E.")
    return valor


def validar_dificuldade(dificuldade: str | None) -> str | None:
    """Garante que a dificuldade seja facil, medio ou dificil."""
    if dificuldade is None:
        return None
    valor = dificuldade.strip().lower()
    if valor not in ("facil", "medio", "dificil"):
        raise ValueError(
            f"Dificuldade invalida: {dificuldade}. Use facil, medio ou dificil."
        )
    return valor


class QuestaoService:
    """Orquestra as regras de negocio usando o repositorio."""

    def __init__(self, repositorio: QuestaoRepository):
        self.repositorio = repositorio

    def criar(self, dados: QuestaoCreate) -> Questao:
        campos = dados.model_dump()
        campos["enunciado"] = normalizar_enunciado(campos["enunciado"])
        campos["tipo"] = validar_tipo(campos["tipo"])
        campos["resposta"] = validar_resposta(campos["resposta"])
        campos["dificuldade"] = validar_dificuldade(campos.get("dificuldade"))
        return self.repositorio.criar(campos)

    def buscar(self, questao_id: int) -> Questao:
        questao = self.repositorio.buscar_por_id(questao_id)
        if questao is None:
            raise QuestaoNaoEncontradaError(f"Questao {questao_id} nao encontrada.")
        return questao

    def listar(
        self,
        ano: int | None = None,
        tipo: str | None = None,
        assunto: str | None = None,
        dificuldade: str | None = None,
    ) -> list[Questao]:
        return self.repositorio.listar(
            ano=ano, tipo=tipo, assunto=assunto, dificuldade=dificuldade
        )

    def atualizar(self, questao_id: int, dados: QuestaoUpdate) -> Questao:
        questao = self.buscar(questao_id)
        enviados = dados.model_dump(exclude_unset=True)
        alteracoes = {}

        if "enunciado" in enviados:
            alteracoes["enunciado"] = normalizar_enunciado(enviados["enunciado"])
        if "tipo" in enviados:
            alteracoes["tipo"] = validar_tipo(enviados["tipo"])
        if "resposta" in enviados:
            alteracoes["resposta"] = validar_resposta(enviados["resposta"])
        if "dificuldade" in enviados:
            alteracoes["dificuldade"] = validar_dificuldade(enviados["dificuldade"])

        for campo in (
            "ano",
            "numero",
            "alternativa_a",
            "alternativa_b",
            "alternativa_c",
            "alternativa_d",
            "alternativa_e",
            "assunto",
            "imagem",
        ):
            if campo in enviados:
                alteracoes[campo] = enviados[campo]

        return self.repositorio.atualizar(questao, alteracoes)

    def remover(self, questao_id: int) -> None:
        self.repositorio.remover(self.buscar(questao_id))

    def contar(
        self,
        ano: int | None = None,
        tipo: str | None = None,
    ) -> int:
        return self.repositorio.contar(ano=ano, tipo=tipo)

    def anos_disponiveis(self) -> list[int]:
        return self.repositorio.anos_disponiveis()

    def estatisticas(self, questao_id: int) -> dict:
        """Estatisticas de como os usuarios ja responderam esta questao."""
        questao = self.buscar(questao_id)
        contagem = self.repositorio.contagem_por_alternativa(questao_id)
        total = sum(contagem.values())

        mais_escolhida = None
        if total > 0:
            mais_escolhida = max(contagem, key=contagem.get)
            if contagem[mais_escolhida] == 0:
                mais_escolhida = None

        taxa_acerto = None
        if total > 0:
            acertos = contagem.get(questao.resposta, 0)
            taxa_acerto = round((acertos / total) * 100, 2)

        return {
            "questao_id": questao_id,
            "total_respostas": total,
            "por_alternativa": contagem,
            "mais_escolhida": mais_escolhida,
            "taxa_acerto": taxa_acerto,
        }

    def cobertura(self) -> dict:
        return self.repositorio.cobertura()

    def reiniciar_cobertura(self) -> dict:
        self.repositorio.reiniciar_ciclo()
        return self.repositorio.cobertura()

    def resumo(self) -> dict:
        """Retorna um resumo do banco de questoes."""
        total = self.repositorio.contar()
        anos = self.repositorio.anos_disponiveis()
        fg = self.repositorio.contar(tipo="FG")
        ce = self.repositorio.contar(tipo="CE")
        return {
            "total": total,
            "formacao_geral": fg,
            "componente_especifico": ce,
            "anos_disponiveis": anos,
        }
