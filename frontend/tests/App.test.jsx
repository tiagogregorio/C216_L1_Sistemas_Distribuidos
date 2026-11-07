import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import App from "../src/App";

describe("App", () => {
	it("renderiza o titulo da plataforma", () => {
		render(<App />);
		expect(screen.getByText("ENADE Study Platform")).toBeInTheDocument();
	});

	it("renderiza os botoes de navegacao", () => {
		render(<App />);
		expect(screen.getByText("Questoes")).toBeInTheDocument();
		expect(screen.getByText("Historico")).toBeInTheDocument();
		expect(screen.getByText("Dashboard")).toBeInTheDocument();
	});

	it("mostra estado de carregamento no dashboard", () => {
		render(<App />);
		expect(screen.getByText("Carregando dashboard...")).toBeInTheDocument();
	});

	it("navega para a pagina de questoes ao clicar", async () => {
		render(<App />);
		const user = userEvent.setup();
		await user.click(screen.getByText("Questoes"));
		expect(screen.getByText("Banco de Questoes")).toBeInTheDocument();
	});

	it("navega para novo simulado ao clicar", async () => {
		render(<App />);
		const user = userEvent.setup();
		const navButtons = screen.getAllByText("Novo Simulado");
		await user.click(navButtons[0]);
		expect(
			screen.getByText("Configure as opcoes e inicie sua prova"),
		).toBeInTheDocument();
	});
});
