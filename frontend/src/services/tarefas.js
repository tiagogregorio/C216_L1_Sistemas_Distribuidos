const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Erro ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function listarTarefas(status) {
  const url = new URL(`${API_URL}/tarefas`);
  if (status) url.searchParams.set("status", status);
  const response = await fetch(url);
  return handleResponse(response);
}

export async function buscarTarefa(id) {
  const response = await fetch(`${API_URL}/tarefas/${id}`);
  return handleResponse(response);
}

export async function criarTarefa(dados) {
  const response = await fetch(`${API_URL}/tarefas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });
  return handleResponse(response);
}

export async function substituirTarefa(id, dados) {
  const response = await fetch(`${API_URL}/tarefas/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });
  return handleResponse(response);
}

export async function atualizarTarefa(id, dados) {
  const response = await fetch(`${API_URL}/tarefas/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
  });
  return handleResponse(response);
}

export async function removerTarefa(id) {
  const response = await fetch(`${API_URL}/tarefas/${id}`, {
    method: "DELETE",
  });
  return handleResponse(response);
}
