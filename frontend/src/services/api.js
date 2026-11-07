const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
	const response = await fetch(`${API_URL}${path}`, {
		headers: { "Content-Type": "application/json", ...options.headers },
		...options,
	});

	if (response.status === 204) return null;

	const data = await response.json();

	if (!response.ok) {
		throw new Error(data.detail || "Erro na requisicao");
	}

	return data;
}

// === Questoes ===

export function listarQuestoes(filtros = {}) {
	const params = new URLSearchParams();
	if (filtros.ano) params.set("ano", filtros.ano);
	if (filtros.tipo) params.set("tipo", filtros.tipo);
	if (filtros.dificuldade) params.set("dificuldade", filtros.dificuldade);
	const query = params.toString();
	return request(`/questoes/${query ? `?${query}` : ""}`);
}

export function buscarQuestao(id) {
	return request(`/questoes/${id}`);
}

export function criarQuestao(dados) {
	return request("/questoes/", { method: "POST", body: JSON.stringify(dados) });
}

export function atualizarQuestao(id, dados) {
	return request(`/questoes/${id}`, {
		method: "PATCH",
		body: JSON.stringify(dados),
	});
}

export function removerQuestao(id) {
	return request(`/questoes/${id}`, { method: "DELETE" });
}

export function resumoQuestoes() {
	return request("/questoes/resumo");
}

export function anosDisponiveis() {
	return request("/questoes/anos");
}

// === Simulados ===

export function listarSimulados() {
	return request("/simulados/");
}

export function criarSimulado(dados) {
	return request("/simulados/", {
		method: "POST",
		body: JSON.stringify(dados),
	});
}

export function buscarSimulado(id) {
	return request(`/simulados/${id}`);
}

export function questoesDoSimulado(id) {
	return request(`/simulados/${id}/questoes`);
}

export function submeterRespostas(id, respostas) {
	return request(`/simulados/${id}/submeter`, {
		method: "POST",
		body: JSON.stringify({ respostas }),
	});
}

export function removerSimulado(id) {
	return request(`/simulados/${id}`, { method: "DELETE" });
}

export function dashboard() {
	return request("/simulados/dashboard");
}
