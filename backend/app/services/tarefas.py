"""Regras de negocio e armazenamento em memoria das tarefas."""

from app.schemas.tarefa import TarefaCreate, TarefaUpdate

PRIORIDADES_VALIDAS = ("baixa", "media", "alta")

_tarefas: dict[int, dict] = {}
_proximo_id = 1


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


def esta_concluida(tarefa: dict) -> bool:
    """Indica se uma tarefa esta no status concluida."""
    return tarefa.get("status") == "concluida"


def resumir_tarefas(tarefas: list[dict]) -> dict:
    """Monta o resumo agregado de uma lista de tarefas."""
    total = len(tarefas)
    concluidas = sum(1 for tarefa in tarefas if esta_concluida(tarefa))
    return {
        "total": total,
        "concluidas": concluidas,
        "progresso": calcular_progresso(total, concluidas),
    }


def resetar() -> None:
    """Limpa o armazenamento em memoria e reinicia o contador de ids."""
    global _proximo_id
    _tarefas.clear()
    _proximo_id = 1


def listar(status: str | None = None) -> list[dict]:
    """Lista as tarefas, opcionalmente filtrando por status."""
    tarefas = list(_tarefas.values())
    if status is None:
        return tarefas
    return [tarefa for tarefa in tarefas if tarefa["status"] == status]


def buscar(tarefa_id: int) -> dict:
    """Retorna uma tarefa pelo id."""
    if tarefa_id not in _tarefas:
        raise TarefaNaoEncontradaError(f"Tarefa {tarefa_id} nao encontrada.")
    return _tarefas[tarefa_id]


def criar(dados: TarefaCreate) -> dict:
    """Cria uma tarefa e devolve o registro criado."""
    global _proximo_id
    tarefa = {
        "id": _proximo_id,
        "titulo": normalizar_titulo(dados.titulo),
        "prioridade": validar_prioridade(dados.prioridade),
        "status": dados.status,
    }
    _tarefas[_proximo_id] = tarefa
    _proximo_id += 1
    return tarefa


def substituir(tarefa_id: int, dados: TarefaCreate) -> dict:
    """Substitui todos os campos de uma tarefa existente."""
    buscar(tarefa_id)
    tarefa = {
        "id": tarefa_id,
        "titulo": normalizar_titulo(dados.titulo),
        "prioridade": validar_prioridade(dados.prioridade),
        "status": dados.status,
    }
    _tarefas[tarefa_id] = tarefa
    return tarefa


def atualizar(tarefa_id: int, dados: TarefaUpdate) -> dict:
    """Atualiza apenas os campos enviados de uma tarefa existente."""
    tarefa = buscar(tarefa_id).copy()
    alteracoes = dados.model_dump(exclude_unset=True)

    if "titulo" in alteracoes:
        tarefa["titulo"] = normalizar_titulo(alteracoes["titulo"])
    if "prioridade" in alteracoes:
        tarefa["prioridade"] = validar_prioridade(alteracoes["prioridade"])
    if "status" in alteracoes:
        tarefa["status"] = alteracoes["status"]

    _tarefas[tarefa_id] = tarefa
    return tarefa


def remover(tarefa_id: int) -> None:
    """Remove uma tarefa existente."""
    buscar(tarefa_id)
    del _tarefas[tarefa_id]


def resumo() -> dict:
    """Devolve o resumo agregado das tarefas armazenadas."""
    return resumir_tarefas(list(_tarefas.values()))
