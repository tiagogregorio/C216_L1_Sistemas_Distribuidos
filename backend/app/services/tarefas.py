"""Regras de negocio das tarefas. Nao conhece HTTP nem SQL."""

from app.models.tarefa import Tarefa
from app.repositories.tarefa import TarefaRepository
from app.schemas.tarefa import TarefaCreate, TarefaUpdate

PRIORIDADES_VALIDAS = ("baixa", "media", "alta")


class TarefaNaoEncontradaError(Exception):
    """Levantada quando o identificador informado nao existe."""


def normalizar_titulo(titulo: str) -> str:
    """Remove espacos nas pontas e espacos duplicados do titulo."""
    limpo = " ".join(titulo.split())
    if not limpo:
        raise ValueError("O titulo nao pode ser vazio.")
    return limpo


def validar_prioridade(prioridade: str) -> str:
    """Normaliza a prioridade e garante que ela seja um valor conhecido."""
    valor = prioridade.strip().lower()
    if valor not in PRIORIDADES_VALIDAS:
        raise ValueError(f"Prioridade invalida: {prioridade}")
    return valor


def calcular_progresso(total: int, concluidas: int) -> float:
    """Calcula o percentual de tarefas concluidas."""
    if total < 0 or concluidas < 0:
        raise ValueError("Os valores nao podem ser negativos.")
    if concluidas > total:
        raise ValueError("Concluidas nao pode ser maior que o total.")
    if total == 0:
        return 0.0
    return round((concluidas / total) * 100, 2)


class TarefaService:
    """Orquestra as regras de negocio usando o repositorio."""

    def __init__(self, repositorio: TarefaRepository):
        self.repositorio = repositorio

    def criar(self, dados: TarefaCreate) -> Tarefa:
        return self.repositorio.criar(
            titulo=normalizar_titulo(dados.titulo),
            prioridade=validar_prioridade(dados.prioridade),
            status=dados.status,
        )

    def buscar(self, tarefa_id: int) -> Tarefa:
        tarefa = self.repositorio.buscar_por_id(tarefa_id)
        if tarefa is None:
            raise TarefaNaoEncontradaError(f"Tarefa {tarefa_id} nao encontrada.")
        return tarefa

    def listar(self, status: str | None = None) -> list[Tarefa]:
        return self.repositorio.listar(status)

    def substituir(self, tarefa_id: int, dados: TarefaCreate) -> Tarefa:
        tarefa = self.buscar(tarefa_id)
        alteracoes = {
            "titulo": normalizar_titulo(dados.titulo),
            "prioridade": validar_prioridade(dados.prioridade),
            "status": dados.status,
        }
        return self.repositorio.atualizar(tarefa, alteracoes)

    def atualizar(self, tarefa_id: int, dados: TarefaUpdate) -> Tarefa:
        tarefa = self.buscar(tarefa_id)
        enviados = dados.model_dump(exclude_unset=True)
        alteracoes = {}

        if "titulo" in enviados:
            alteracoes["titulo"] = normalizar_titulo(enviados["titulo"])
        if "prioridade" in enviados:
            alteracoes["prioridade"] = validar_prioridade(enviados["prioridade"])
        if "status" in enviados:
            alteracoes["status"] = enviados["status"]

        return self.repositorio.atualizar(tarefa, alteracoes)

    def remover(self, tarefa_id: int) -> None:
        self.repositorio.remover(self.buscar(tarefa_id))

    def resumo(self) -> dict:
        """Resumo agregado, contado diretamente no banco."""
        total = self.repositorio.contar()
        concluidas = self.repositorio.contar("concluida")
        return {
            "total": total,
            "concluidas": concluidas,
            "progresso": calcular_progresso(total, concluidas),
        }
