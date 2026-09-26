"""Regras de negocio de tarefas, isoladas da camada HTTP."""

PRIORIDADES_VALIDAS = ("baixa", "media", "alta")


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
