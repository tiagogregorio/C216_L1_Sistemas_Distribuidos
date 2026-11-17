import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import QuizQuestao from "../src/components/QuizQuestao";
import { SoundProvider } from "../src/sound/SoundContext";

const QUESTAO = {
	id: 1,
	ano: 2023,
	numero: 13,
	enunciado: "Enunciado de teste da questao.",
	alternativa_a: "A",
	alternativa_b: "B",
	alternativa_c: "C",
	alternativa_d: "D",
	alternativa_e: "E",
	resposta: "A",
	assunto: "Grafos",
	dificuldade: "facil",
	fonte: null,
	imagem: null,
	pagina_original: "data:image/jpeg;base64,abc",
};

function renderizar(questao) {
	return render(
		<SoundProvider>
			<QuizQuestao
				questao={questao}
				numero={1}
				total={1}
				respostaSalva={null}
				respondidas={[false]}
				onResponder={vi.fn()}
			/>
		</SoundProvider>,
	);
}

describe("QuizQuestao - pagina original do PDF", () => {
	it("abre e fecha a pagina original quando ela esta anexada", async () => {
		renderizar(QUESTAO);
		const user = userEvent.setup();
		expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

		await user.click(screen.getByRole("button", { name: /Ver pagina do PDF/ }));
		expect(screen.getByRole("dialog")).toBeInTheDocument();
		expect(
			screen.getByAltText("Pagina original da prova em PDF"),
		).toHaveAttribute("src", QUESTAO.pagina_original);

		await user.click(screen.getByRole("button", { name: /Fechar/ }));
		expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
	});

	it("fecha com a tecla Esc", async () => {
		renderizar(QUESTAO);
		const user = userEvent.setup();
		await user.click(screen.getByRole("button", { name: /Ver pagina do PDF/ }));
		await user.keyboard("{Escape}");
		expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
	});

	it("desabilita o botao e explica o motivo quando nao ha pagina anexada", () => {
		renderizar({ ...QUESTAO, pagina_original: null });
		const botao = screen.getByRole("button", { name: /Ver pagina do PDF/ });
		expect(botao).toBeDisabled();
		expect(botao).toHaveAttribute(
			"title",
			expect.stringContaining("Reimporte"),
		);
	});
});
