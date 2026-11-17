import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import AjudasQuiz from "../src/components/AjudasQuiz";
import { SoundProvider } from "../src/sound/SoundContext";

vi.mock("../src/services/api", () => ({
	assistenteIA: vi.fn().mockResolvedValue({
		explicacao: "A alternativa B esta correta porque usa LIFO.",
	}),
}));

function renderizar(props = {}) {
	const padrao = {
		questaoId: 1,
		respostaCorreta: "C",
		confirmada: false,
		cartasUsada: false,
		onUsarCartas: vi.fn(),
		universitariosUsada: false,
		onUsarUniversitarios: vi.fn(),
		iaUsada: false,
		onUsarIA: vi.fn(),
	};
	return render(
		<SoundProvider>
			<AjudasQuiz {...padrao} {...props} />
		</SoundProvider>,
	);
}

describe("AjudasQuiz", () => {
	it("renderiza os tres botoes de ajuda", () => {
		renderizar();
		expect(screen.getByText("Cartas")).toBeInTheDocument();
		expect(screen.getByText("Universitarios")).toBeInTheDocument();
		expect(screen.getByText("Assistente IA")).toBeInTheDocument();
	});

	it("chama onUsarCartas ao clicar em Cartas", async () => {
		const onUsarCartas = vi.fn();
		renderizar({ onUsarCartas });
		const user = userEvent.setup();
		await user.click(screen.getByText("Cartas"));
		expect(onUsarCartas).toHaveBeenCalledTimes(1);
	});

	it("mostra a estatistica apontando sempre para a resposta correta", async () => {
		// A visibilidade do painel depende da prop universitariosUsada, que no
		// uso real e controlada pelo componente pai (QuizQuestao).
		function Wrapper() {
			const [usada, setUsada] = useState(false);
			return (
				<SoundProvider>
					<AjudasQuiz
						questaoId={1}
						respostaCorreta="D"
						confirmada={false}
						cartasUsada={false}
						onUsarCartas={() => {}}
						universitariosUsada={usada}
						onUsarUniversitarios={() => setUsada(true)}
						iaUsada={false}
						onUsarIA={() => {}}
					/>
				</SoundProvider>
			);
		}
		render(<Wrapper />);
		const user = userEvent.setup();
		await user.click(screen.getByText("Universitarios"));

		expect(
			screen.getByText((texto) => texto.includes("alternativa")),
		).toBeInTheDocument();
		const destaque = screen.getByText("D", { selector: "strong" });
		expect(destaque).toBeInTheDocument();
	});

	it("busca e exibe a explicacao do assistente de IA", async () => {
		function Wrapper() {
			const [usada, setUsada] = useState(false);
			return (
				<SoundProvider>
					<AjudasQuiz
						questaoId={7}
						respostaCorreta="B"
						confirmada={false}
						cartasUsada={false}
						onUsarCartas={() => {}}
						universitariosUsada={false}
						onUsarUniversitarios={() => {}}
						iaUsada={usada}
						onUsarIA={() => setUsada(true)}
					/>
				</SoundProvider>
			);
		}
		render(<Wrapper />);
		const user = userEvent.setup();
		await user.click(screen.getByText("Assistente IA"));

		await waitFor(() => {
			expect(
				screen.getByText(/A alternativa B esta correta/),
			).toBeInTheDocument();
		});
	});

	it("desabilita os botoes quando a resposta ja foi confirmada", () => {
		renderizar({ confirmada: true });
		expect(screen.getByText("Cartas").closest("button")).toBeDisabled();
		expect(screen.getByText("Universitarios").closest("button")).toBeDisabled();
		expect(screen.getByText("Assistente IA").closest("button")).toBeDisabled();
	});
});
