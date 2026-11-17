export function validarQuestao(dados) {
	const erros = {};

	if (!dados.enunciado || dados.enunciado.trim().length < 10) {
		erros.enunciado = "O enunciado deve ter pelo menos 10 caracteres.";
	}
	if (!dados.ano || dados.ano < 2004 || dados.ano > 2030) {
		erros.ano = "Ano invalido.";
	}
	if (!dados.numero || dados.numero < 1) {
		erros.numero = "Numero da questao invalido.";
	}
	if (!["FG", "CE"].includes(dados.tipo)) {
		erros.tipo = "Tipo deve ser FG ou CE.";
	}
	if (!["A", "B", "C", "D", "E"].includes(dados.resposta)) {
		erros.resposta = "Resposta deve ser A, B, C, D ou E.";
	}

	for (const letra of ["a", "b", "c", "d", "e"]) {
		const campo = `alternativa_${letra}`;
		if (!dados[campo] || dados[campo].trim().length < 1) {
			erros[campo] = `Alternativa ${letra.toUpperCase()} e obrigatoria.`;
		}
	}

	return erros;
}

export function validarSimulado(dados) {
	const erros = {};

	if (!dados.nome || dados.nome.trim().length < 3) {
		erros.nome = "O nome deve ter pelo menos 3 caracteres.";
	}
	if (!dados.quantidade || dados.quantidade < 1 || dados.quantidade > 50) {
		erros.quantidade = "Quantidade deve ser entre 1 e 50.";
	}

	return erros;
}
