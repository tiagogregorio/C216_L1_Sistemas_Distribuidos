import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../../src/App";
import * as api from "../../src/services/tarefas";

vi.mock("../../src/services/tarefas");

const tarefaMock = {
  id: 1,
  titulo: "Estudar SQLAlchemy",
  prioridade: "alta",
  status: "pendente",
};

describe("App — integração com API mockada", () => {
  beforeEach(() => {
    api.listarTarefas.mockResolvedValue([]);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("exibe mensagem vazia quando a API retorna lista vazia", async () => {
    render(<App />);
    await waitFor(() => {
      expect(
        screen.getByText("Nenhuma tarefa cadastrada."),
      ).toBeInTheDocument();
    });
  });

  it("exibe tarefas retornadas pela API", async () => {
    api.listarTarefas.mockResolvedValue([tarefaMock]);
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText("Estudar SQLAlchemy")).toBeInTheDocument();
    });
  });

  it("cria uma tarefa e a exibe na lista", async () => {
    const user = userEvent.setup();
    api.criarTarefa.mockResolvedValue(tarefaMock);
    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("Nenhuma tarefa cadastrada."),
      ).toBeInTheDocument();
    });

    await user.type(screen.getByLabelText("Título"), "Estudar SQLAlchemy");
    await user.click(screen.getByRole("button", { name: "Adicionar" }));

    await waitFor(() => {
      expect(screen.getByText("Estudar SQLAlchemy")).toBeInTheDocument();
    });
    expect(api.criarTarefa).toHaveBeenCalledWith({
      titulo: "Estudar SQLAlchemy",
      prioridade: "media",
    });
  });

  it("remove uma tarefa da lista", async () => {
    api.listarTarefas.mockResolvedValue([tarefaMock]);
    api.removerTarefa.mockResolvedValue(null);
    const user = userEvent.setup();
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Estudar SQLAlchemy")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Excluir" }));

    await waitFor(() => {
      expect(
        screen.getByText("Nenhuma tarefa cadastrada."),
      ).toBeInTheDocument();
    });
  });

  it("exibe mensagem de erro quando a API falha", async () => {
    api.listarTarefas.mockRejectedValue(new Error("Network Error"));
    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Falha ao carregar tarefas",
      );
    });
  });
});
