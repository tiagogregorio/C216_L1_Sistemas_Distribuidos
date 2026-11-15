const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// O FastAPI devolve "detail" como texto (nossos erros) ou como lista (validacao 422).
function mensagemDeErro(detail, status) {
	if (typeof detail === "string") return detail;
	if (Array.isArray(detail)) return detail.map((d) => d.msg).join("; ");
	return `Erro na requisicao (HTTP ${status})`;
}

// fetch rejeitado = o navegador nem recebeu resposta (servidor fora do ar,
// reiniciando, ou erro 500 sem CORS). O texto original ("NetworkError...",
// "Failed to fetch") nao ajuda ninguem, entao trocamos por algo acionavel.
function erroDeRede() {
	const erro = new Error(
		"Nao foi possivel falar com o servidor (backend fora do ar, reiniciando ou com erro). " +
			"No terminal, rode 'docker compose ps' e 'docker compose logs backend --tail=60'.",
	);
	erro.rede = true;
	return erro;
}

async function enviar(url, init) {
	let response;
	try {
		response = await fetch(url, init);
	} catch {
		throw erroDeRede();
	}

	if (response.status === 204) return null;

	const data = await response.json().catch(() => null);

	if (!response.ok) {
		const erro = new Error(mensagemDeErro(data?.detail, response.status));
		erro.status = response.status;
		throw erro;
	}

	return data;
}

async function request(path, options = {}) {
	return enviar(`${API_URL}${path}`, {
		headers: { "Content-Type": "application/json", ...options.headers },
		...options,
	});
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

export function estatisticasQuestao(id) {
	return request(`/questoes/${id}/estatisticas`);
}

export async function importarPdf(arquivo, ano, inicioCE) {
	const formData = new FormData();
	formData.append("arquivo", arquivo);
	formData.append("ano", ano);
	formData.append("inicio_ce", inicioCE);

	// Upload multipart: nao define Content-Type manualmente, o navegador
	// precisa gerar o boundary sozinho.
	return enviar(`${API_URL}/questoes/importar-pdf`, {
		method: "POST",
		body: formData,
	});
}

export function classificarQuestoesLote(questoes) {
	return request("/questoes/classificar-lote", {
		method: "POST",
		body: JSON.stringify({ questoes }),
	});
}

export function statusIA(testar = false) {
	return request(`/questoes/ia/status${testar ? "?testar=true" : ""}`);
}

export function assistenteIA(id) {
	return request(`/questoes/${id}/assistente-ia`, { method: "POST" });
}

export function coberturaQuestoes() {
	return request("/questoes/cobertura");
}

export function reiniciarCobertura() {
	return request("/questoes/cobertura/reiniciar", { method: "POST" });
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

export function relatorioSimulados() {
	return request("/simulados/relatorio");
}

export function dashboard() {
	return request("/simulados/dashboard");
}
