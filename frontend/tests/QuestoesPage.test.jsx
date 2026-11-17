import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import QuestoesPage from "../src/pages/QuestoesPage";
import * as api from "../src/services/api";

vi.mock("../src/services/api");

const resumo = {
	id: 7,
	ano: 2019,
	numero: 3,
	tipo: "CE",
	dificuldade: "medio",
	assunto: "Grafos",
};

const completa = {
	...resumo,
	enunciado: "Enunciado completo da questao de grafos.",
	alternativa_a: "A1",
	alternativa_b: "B1",
	alternativa_c: "C1",
	alternativa_d: "D1",
	alternativa_e: "E1",
	resposta: "B",
	imagem: null,
	fonte: null,
	pagina_original: "data:image/png;base64,AAAA",
};

describe("QuestoesPage - editar", () => {
	beforeEach(() => {
		vi.resetAllMocks();
		api.listarQuestoes.mockResolvedValue([resumo]);
		api.buscarQuestao.mockResolvedValue(completa);
		api.atualizarQuestao.mockResolvedValue(completa);
	});

	it("abre o formulario preenchido ao clicar em Editar", async () => {
		render(<QuestoesPage />);
		const user = userEvent.setup();

		await user.click(await screen.findByRole("button", { name: "Editar" }));

		expect(api.buscarQuestao).toHaveBeenCalledWith(7);
		expect(await screen.findByText(/Editar Questao/)).toBeInTheDocument();
		expect(
			screen.getByDisplayValue("Enunciado completo da questao de grafos."),
		).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Atualizar Questao" }),
		).toBeInTheDocument();
	});

	it("envia a atualizacao sem id nem pagina original e recarrega a lista", async () => {
		render(<QuestoesPage />);
		const user = userEvent.setup();

		await user.click(await screen.findByRole("button", { name: "Editar" }));
		const campo = await screen.findByDisplayValue(
			"Enunciado completo da questao de grafos.",
		);
		fireEvent.change(campo, {
			target: { value: "Enunciado editado pelo teste automatizado." },
		});
		await user.click(screen.getByRole("button", { name: "Atualizar Questao" }));

		await waitFor(() => expect(api.atualizarQuestao).toHaveBeenCalled());
		const [id, corpo] = api.atualizarQuestao.mock.calls[0];
		expect(id).toBe(7);
		expect(corpo.enunciado).toBe("Enunciado editado pelo teste automatizado.");
		expect(corpo).not.toHaveProperty("id");
		expect(corpo).not.toHaveProperty("pagina_original");
		await waitFor(() => expect(api.listarQuestoes).toHaveBeenCalledTimes(2));
		expect(
			await screen.findByText("Questao atualizada com sucesso."),
		).toBeInTheDocument();
	});

	it("Cancelar fecha o formulario sem salvar", async () => {
		render(<QuestoesPage />);
		const user = userEvent.setup();

		await user.click(await screen.findByRole("button", { name: "Editar" }));
		await user.click(await screen.findByRole("button", { name: "Cancelar" }));

		expect(screen.queryByText(/Editar Questao/)).not.toBeInTheDocument();
		expect(api.atualizarQuestao).not.toHaveBeenCalled();
	});
});
