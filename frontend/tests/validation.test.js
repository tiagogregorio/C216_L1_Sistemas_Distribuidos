import { describe, expect, it } from "vitest";
import { validarQuestao, validarSimulado } from "../src/validation";

describe("validarQuestao", () => {
	const questaoValida = {
		ano: 2019,
		numero: 1,
		tipo: "CE",
		enunciado: "Enunciado valido com mais de dez caracteres.",
		alternativa_a: "A",
		alternativa_b: "B",
		alternativa_c: "C",
		alternativa_d: "D",
		alternativa_e: "E",
		resposta: "A",
	};

	it("retorna objeto vazio para questao valida", () => {
		const erros = validarQuestao(questaoValida);
		expect(Object.keys(erros)).toHaveLength(0);
	});

	it("retorna erro para enunciado curto", () => {
		const erros = validarQuestao({ ...questaoValida, enunciado: "curto" });
		expect(erros.enunciado).toBeDefined();
	});

	it("retorna erro para tipo invalido", () => {
		const erros = validarQuestao({ ...questaoValida, tipo: "XX" });
		expect(erros.tipo).toBeDefined();
	});

	it("retorna erro para resposta invalida", () => {
		const erros = validarQuestao({ ...questaoValida, resposta: "F" });
		expect(erros.resposta).toBeDefined();
	});

	it("retorna erro para alternativa vazia", () => {
		const erros = validarQuestao({ ...questaoValida, alternativa_a: "" });
		expect(erros.alternativa_a).toBeDefined();
	});
});

describe("validarSimulado", () => {
	it("retorna objeto vazio para simulado valido", () => {
		const erros = validarSimulado({ nome: "Revisao", quantidade: 10 });
		expect(Object.keys(erros)).toHaveLength(0);
	});

	it("retorna erro para nome curto", () => {
		const erros = validarSimulado({ nome: "ab", quantidade: 10 });
		expect(erros.nome).toBeDefined();
	});

	it("retorna erro para quantidade zero", () => {
		const erros = validarSimulado({ nome: "Teste", quantidade: 0 });
		expect(erros.quantidade).toBeDefined();
	});
});
