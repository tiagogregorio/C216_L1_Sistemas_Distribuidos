const BADGE_COLORS = {
  baixa: "bg-green-100 text-green-800",
  media: "bg-yellow-100 text-yellow-800",
  alta: "bg-red-100 text-red-800",
};

export function TarefaList({ tarefas, onToggle, onDelete }) {
  if (tarefas.length === 0) {
    return <p className="text-slate-600">Nenhuma tarefa cadastrada.</p>;
  }

  return (
    <ul className="space-y-2">
      {tarefas.map((t) => (
        <li
          key={t.id}
          className="flex items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div className="min-w-0 flex-1">
            <p
              className={`font-medium ${t.status === "concluida" ? "line-through opacity-60" : ""}`}
            >
              {t.titulo}
            </p>
            <span
              className={`mt-1 inline-block rounded px-2 py-0.5 text-xs font-medium ${BADGE_COLORS[t.prioridade]}`}
            >
              {t.prioridade}
            </span>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onToggle(t)}
              className="rounded border border-slate-300 px-3 py-1 text-sm hover:bg-slate-50"
            >
              {t.status === "pendente" ? "Concluir" : "Reabrir"}
            </button>
            <button
              type="button"
              onClick={() => onDelete(t.id)}
              className="rounded border border-red-300 px-3 py-1 text-sm text-red-700 hover:bg-red-50"
            >
              Excluir
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}
