import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TarefaForm } from "../../src/components/TarefaForm";

describe("TarefaForm", () => {
  it("mostra erro e não chama onAdd com título vazio", async () => {
    const user = userEvent.setup();
    const onAdd = vi.fn();
    render(<TarefaForm onAdd={onAdd} loading={false} />);

    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "O título é obrigatório.",
    );
    expect(onAdd).not.toHaveBeenCalled();
  });

  it("chama onAdd com os valores e limpa o formulário", async () => {
    const user = userEvent.setup();
    const onAdd = vi.fn();
    render(<TarefaForm onAdd={onAdd} loading={false} />);

    await user.type(screen.getByLabelText("Título"), "Estudar SQLAlchemy");
    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    expect(onAdd).toHaveBeenCalledWith({
      titulo: "Estudar SQLAlchemy",
      prioridade: "media",
    });
    expect(screen.getByLabelText("Título")).toHaveValue("");
  });
});
