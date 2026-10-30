import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import App from "../../src/App";

describe("App — formulário + listagem", () => {
  it("exibe mensagem vazia ao iniciar", () => {
    render(<App />);
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  });

  it("cadastra um item e o exibe na lista", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText("Nome"), "Notebook");
    await user.type(screen.getByLabelText("Descrição"), "14 polegadas");
    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(screen.getByText("Notebook")).toBeInTheDocument();
    expect(screen.getByText("14 polegadas")).toBeInTheDocument();
    expect(
      screen.queryByText("Nenhum item cadastrado."),
    ).not.toBeInTheDocument();
  });

  it("cadastra múltiplos itens", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.type(screen.getByLabelText("Nome"), "Item 1");
    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    await user.type(screen.getByLabelText("Nome"), "Item 2");
    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    const listItems = screen.getAllByRole("listitem");
    expect(listItems).toHaveLength(2);
  });

  it("não cadastra item com nome vazio", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "O nome é obrigatório.",
    );
    expect(screen.getByText("Nenhum item cadastrado.")).toBeInTheDocument();
  });
});
