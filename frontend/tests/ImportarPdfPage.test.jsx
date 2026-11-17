import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ImportarPdfPage from "../src/pages/ImportarPdfPage";
import * as api from "../src/services/api";

vi.mock("../src/services/api", () => ({
	importarPdf: vi.fn(),
	criarQuestao: vi.fn(),
	atualizarQuestao: vi.fn(),
	listarQuestoes: vi.fn(),
	classificarQuestoesLote: vi.fn(),
	statusIA: vi.fn(),
}));

const PAGINA = "data:image/jpeg;base64,abc";

const QUESTAO_IMPORTADA = {
	ano: 2023,
	numero: 10,
	tipo: "CE",
	enunciado: "Enunciado de teste",
	alternativa_a: "A",
	alternativa_b: "B",
	alternativa_c: "C",
	alternativa_d: "D",
	alternativa_e: "E",
	resposta: "A",
	assunto: "",
	dificuldade: "medio",
	pagina: 1,
	alternativas_incompletas: false,
};

beforeEach(() => {
	vi.resetAllMocks();
	api.statusIA.mockResolvedValue({ configurada: true, modelo: "gemini-teste" });
	api.importarPdf.mockResolvedValue({
		paginas: [PAGINA],
		questoes: [QUESTAO_IMPORTADA],
	});
	api.listarQuestoes.mockResolvedValue([]);
	api.criarQuestao.mockResolvedValue({ id: 1 });
	api.atualizarQuestao.mockResolvedValue({ id: 5 });
	api.classificarQuestoesLote.mockResolvedValue({
		resultados: [{ assunto: "Grafos", dificuldade: "dificil" }],
	});
	vi.spyOn(window, "confirm").mockReturnValue(true);
});

async function importarUmPdf() {
	render(<ImportarPdfPage onFechar={() => {}} />);
	const user = userEvent.setup();
	await user.upload(
		screen.getByLabelText(/Arquivo PDF/),
		new File(["conteudo"], "prova.pdf", { type: "application/pdf" }),
	);
	fireEvent.submit(
		screen.getByRole("button", { name: "Importar" }).closest("form"),
	);
	await screen.findByText("Questao 10");
	return user;
}

describe("ImportarPdfPage", () => {
	it("mostra o formulario inicial de upload", async () => {
		render(<ImportarPdfPage onFechar={() => {}} />);
		expect(screen.getByText("Importar questoes de um PDF")).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Importar" })).toBeDisabled();
		expect(await screen.findByText(/IA \(Gemini\) configurada/)).toBeVisible();
	});

	it("avisa com clareza quando a IA nao esta configurada", async () => {
		api.statusIA.mockResolvedValue({ configurada: false, modelo: "x" });
		render(<ImportarPdfPage onFechar={() => {}} />);
		expect(await screen.findByText(/NAO configurada/)).toBeVisible();
	});

	it("processa o PDF e mostra os rascunhos para revisao", async () => {
		await importarUmPdf();
		expect(screen.getByDisplayValue("Enunciado de teste")).toBeInTheDocument();
	});

	it("salvar todas anexa a pagina original a cada questao", async () => {
		const user = await importarUmPdf();
		await user.click(screen.getByRole("button", { name: /Salvar todas/ }));

		await waitFor(() => {
			expect(api.criarQuestao).toHaveBeenCalledWith(
				expect.objectContaining({ numero: 10, pagina_original: PAGINA }),
			);
		});
		expect(await screen.findByText(/1 nova\(s\) salva\(s\)/)).toBeVisible();
	});

	it("nao cria duplicata: questao existente so recebe a pagina", async () => {
		api.listarQuestoes.mockResolvedValue([
			{ id: 5, ano: 2023, numero: 10, fonte: null },
		]);
		const user = await importarUmPdf();
		expect(screen.getByText(/Ja existe no banco/)).toBeVisible();

		await user.click(screen.getByRole("button", { name: /Salvar todas/ }));

		await waitFor(() => {
			expect(api.atualizarQuestao).toHaveBeenCalledWith(5, {
				pagina_original: PAGINA,
			});
		});
		expect(api.criarQuestao).not.toHaveBeenCalled();
		expect(
			await screen.findByText(/1 existente\(s\) com pagina anexada/),
		).toBeVisible();
	});

	it("classifica via IA e preenche o assunto", async () => {
		const user = await importarUmPdf();
		await user.click(
			screen.getByRole("button", { name: /Classificar via IA/ }),
		);

		expect(await screen.findByDisplayValue("Grafos")).toBeInTheDocument();
		expect(api.classificarQuestoesLote).toHaveBeenCalledTimes(1);
	});

	it("mostra o erro da IA em vez de falhar em silencio", async () => {
		api.classificarQuestoesLote.mockRejectedValue(
			new Error("O limite de uso gratuito do Gemini foi atingido."),
		);
		const user = await importarUmPdf();
		await user.click(
			screen.getByRole("button", { name: /Classificar via IA/ }),
		);

		expect(await screen.findByRole("alert")).toHaveTextContent(
			/limite de uso gratuito/,
		);
	});
});

function questao(numero, extra = {}) {
	return { ...QUESTAO_IMPORTADA, numero, ...extra };
}

describe("ImportarPdfPage - revisao e falhas", () => {
	it("nao salva em lote a questao sem texto extraido", async () => {
		api.importarPdf.mockResolvedValue({
			paginas: [PAGINA],
			questoes: [
				questao(10),
				questao(11, {
					enunciado: "",
					alternativa_a: "",
					alternativa_b: "",
					alternativa_c: "",
					alternativa_d: "",
					alternativa_e: "",
					sem_texto: true,
					pagina: null,
					alternativas_incompletas: true,
				}),
			],
		});
		const user = await importarUmPdf();
		expect(screen.getByText(/Texto nao extraido/)).toBeVisible();

		await user.click(
			screen.getByRole("button", { name: /Salvar todas \(1\)/ }),
		);

		await waitFor(() => expect(api.criarQuestao).toHaveBeenCalledTimes(1));
		expect(api.criarQuestao).toHaveBeenCalledWith(
			expect.objectContaining({ numero: 10 }),
		);
		expect(await screen.findByText(/1 pulada\(s\)/)).toBeVisible();
	});

	it("pula a questao com possivel mistura, mas deixa salvar uma a uma", async () => {
		api.importarPdf.mockResolvedValue({
			paginas: [PAGINA],
			questoes: [questao(10, { mistura_possivel: true }), questao(12)],
		});
		const user = await importarUmPdf();
		expect(
			screen.getByText(/Pode conter texto da questao seguinte/),
		).toBeVisible();

		await user.click(screen.getByRole("button", { name: /Salvar todas/ }));
		await waitFor(() => expect(api.criarQuestao).toHaveBeenCalledTimes(1));
		expect(api.criarQuestao).toHaveBeenCalledWith(
			expect.objectContaining({ numero: 12 }),
		);

		// Depois de revisada pelo usuario, salva individualmente.
		await user.click(screen.getByRole("button", { name: "Salvar questao" }));
		await waitFor(() => expect(api.criarQuestao).toHaveBeenCalledTimes(2));
		expect(api.criarQuestao).toHaveBeenLastCalledWith(
			expect.objectContaining({ numero: 10 }),
		);
	});

	it("interrompe o envio quando o servidor para de responder", async () => {
		api.importarPdf.mockResolvedValue({
			paginas: [PAGINA],
			questoes: [10, 11, 12, 13, 14].map((n) => questao(n)),
		});
		api.criarQuestao.mockRejectedValue(
			Object.assign(new Error("Nao foi possivel falar com o servidor"), {
				rede: true,
			}),
		);
		const user = await importarUmPdf();

		await user.click(screen.getByRole("button", { name: /Salvar todas/ }));

		expect(await screen.findByText(/Envio interrompido/)).toBeVisible();
		expect(api.criarQuestao).toHaveBeenCalledTimes(3);
	});

	it("nao deixa salvar em lote enquanto a IA classifica", async () => {
		let liberar;
		api.classificarQuestoesLote.mockReturnValue(
			new Promise((resolve) => {
				liberar = resolve;
			}),
		);
		const user = await importarUmPdf();

		await user.click(
			screen.getByRole("button", { name: /Classificar via IA/ }),
		);
		expect(screen.getByRole("button", { name: /Salvar todas/ })).toBeDisabled();

		liberar({ resultados: [{ assunto: "Grafos", dificuldade: "dificil" }] });
		expect(await screen.findByDisplayValue("Grafos")).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /Salvar todas/ })).toBeEnabled();
	});
});
