/**
 * Persistencia local do progresso de um simulado em andamento, para que
 * atualizar a pagina (F5) continue de onde o usuario parou, em vez de
 * voltar para o inicio.
 */

const PREFIXO = "enade:progresso-simulado:";

function chave(simuladoId) {
	return `${PREFIXO}${simuladoId}`;
}

export function lerProgresso(simuladoId) {
	try {
		const bruto = localStorage.getItem(chave(simuladoId));
		return bruto ? JSON.parse(bruto) : null;
	} catch {
		return null;
	}
}

export function salvarProgresso(simuladoId, progresso) {
	try {
		localStorage.setItem(chave(simuladoId), JSON.stringify(progresso));
	} catch {
		// localStorage indisponivel (modo privado, por exemplo); ignora.
	}
}

export function limparProgresso(simuladoId) {
	localStorage.removeItem(chave(simuladoId));
}
