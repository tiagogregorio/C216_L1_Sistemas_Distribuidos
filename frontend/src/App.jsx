import { useCallback, useEffect, useState } from "react";
import { TarefaForm } from "./components/TarefaForm";
import { TarefaList } from "./components/TarefaList";
import {
  atualizarTarefa,
  criarTarefa,
  listarTarefas,
  removerTarefa,
} from "./services/tarefas";

export default function App() {
  const [tarefas, setTarefas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const carregarTarefas = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listarTarefas();
      setTarefas(data);
    } catch (err) {
      setError(`Falha ao carregar tarefas: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    carregarTarefas();
  }, [carregarTarefas]);

  async function handleAdd(values) {
    setSaving(true);
    setError(null);
    try {
      const nova = await criarTarefa(values);
      setTarefas((current) => [...current, nova]);
    } catch (err) {
      setError(`Falha ao criar tarefa: ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  async function handleToggle(tarefa) {
    setError(null);
    const novoStatus = tarefa.status === "pendente" ? "concluida" : "pendente";
    try {
      const atualizada = await atualizarTarefa(tarefa.id, {
        status: novoStatus,
      });
      setTarefas((current) =>
        current.map((t) => (t.id === tarefa.id ? atualizada : t)),
      );
    } catch (err) {
      setError(`Falha ao atualizar tarefa: ${err.message}`);
    }
  }

  async function handleDelete(id) {
    setError(null);
    try {
      await removerTarefa(id);
      setTarefas((current) => current.filter((t) => t.id !== id));
    } catch (err) {
      setError(`Falha ao remover tarefa: ${err.message}`);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-xl space-y-6 p-4 sm:p-6">
      <h1 className="text-3xl font-bold">Gerenciador de Tarefas</h1>

      {error && (
        <div
          role="alert"
          className="rounded bg-red-50 p-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      <TarefaForm onAdd={handleAdd} loading={saving} />

      <section aria-labelledby="tarefas-heading" className="space-y-3">
        <h2 id="tarefas-heading" className="text-xl font-semibold">
          Tarefas cadastradas
        </h2>
        {loading ? (
          <p className="text-slate-600">Carregando...</p>
        ) : (
          <TarefaList
            tarefas={tarefas}
            onToggle={handleToggle}
            onDelete={handleDelete}
          />
        )}
      </section>
    </main>
  );
}
