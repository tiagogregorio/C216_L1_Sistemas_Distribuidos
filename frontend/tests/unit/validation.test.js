import { describe, expect, it } from "vitest";
import { TITULO_MAX, TITULO_MIN, validateTarefa } from "../../src/validation";

describe("validateTarefa", () => {
  it("rejeita título vazio ou só com espaços", () => {
    const { errors } = validateTarefa({ titulo: "   ", prioridade: "media" });
    expect(errors.titulo).toBe("O título é obrigatório.");
  });

  it("rejeita título com menos de 3 caracteres", () => {
    const { errors } = validateTarefa({ titulo: "ab", prioridade: "media" });
    expect(errors.titulo).toBe(
      `O título deve ter no mínimo ${TITULO_MIN} caracteres.`,
    );
  });

  it("rejeita título com mais de 80 caracteres", () => {
    const longTitle = "a".repeat(TITULO_MAX + 1);
    const { errors } = validateTarefa({
      titulo: longTitle,
      prioridade: "media",
    });
    expect(errors.titulo).toBe(
      `O título deve ter no máximo ${TITULO_MAX} caracteres.`,
    );
  });

  it("aceita título válido e faz trim", () => {
    const { errors, values } = validateTarefa({
      titulo: "  Estudar SQLAlchemy  ",
      prioridade: "alta",
    });
    expect(Object.keys(errors)).toHaveLength(0);
    expect(values.titulo).toBe("Estudar SQLAlchemy");
    expect(values.prioridade).toBe("alta");
  });

  it("rejeita prioridade inválida", () => {
    const { errors } = validateTarefa({
      titulo: "Tarefa",
      prioridade: "urgente",
    });
    expect(errors.prioridade).toBe("Prioridade inválida.");
  });
});
