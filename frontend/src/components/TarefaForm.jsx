import { useState } from "react";
import { PRIORIDADES, validateTarefa } from "../validation";

export function TarefaForm({ onAdd, loading }) {
  const [titulo, setTitulo] = useState("");
  const [prioridade, setPrioridade] = useState("media");
  const [errors, setErrors] = useState({});

  async function handleSubmit(event) {
    event.preventDefault();
    const result = validateTarefa({ titulo, prioridade });
    setErrors(result.errors);
    if (Object.keys(result.errors).length > 0) return;

    await onAdd(result.values);
    setTitulo("");
    setPrioridade("media");
  }

  return (
    <form
      onSubmit={handleSubmit}
      noValidate
      className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="space-y-1">
        <label htmlFor="tarefa-titulo" className="block text-sm font-medium">
          Título
        </label>
        <input
          id="tarefa-titulo"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          aria-invalid={errors.titulo ? "true" : "false"}
          aria-describedby={errors.titulo ? "tarefa-titulo-error" : undefined}
          className="w-full rounded border border-slate-300 p-2"
        />
        {errors.titulo && (
          <p
            id="tarefa-titulo-error"
            role="alert"
            className="text-sm text-red-700"
          >
            {errors.titulo}
          </p>
        )}
      </div>

      <div className="space-y-1">
        <label
          htmlFor="tarefa-prioridade"
          className="block text-sm font-medium"
        >
          Prioridade
        </label>
        <select
          id="tarefa-prioridade"
          value={prioridade}
          onChange={(e) => setPrioridade(e.target.value)}
          className="w-full rounded border border-slate-300 p-2"
        >
          {PRIORIDADES.map((p) => (
            <option key={p} value={p}>
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50 sm:w-auto"
      >
        {loading ? "Salvando..." : "Adicionar"}
      </button>
    </form>
  );
}
