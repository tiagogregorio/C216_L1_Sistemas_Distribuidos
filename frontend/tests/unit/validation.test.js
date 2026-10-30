import { describe, expect, it } from "vitest";
import { NAME_MAX_LENGTH, validateItem } from "../../src/validation";

describe("validateItem", () => {
  it("rejeita nome vazio ou só com espaços", () => {
    const { errors } = validateItem({ name: "   ", description: "" });
    expect(errors.name).toBe("O nome é obrigatório.");
  });

  it("rejeita nome com mais de 100 caracteres", () => {
    const longName = "a".repeat(NAME_MAX_LENGTH + 1);
    const { errors } = validateItem({ name: longName, description: "" });
    expect(errors.name).toBe(
      `O nome deve ter no máximo ${NAME_MAX_LENGTH} caracteres.`,
    );
  });

  it("aceita nome válido e faz trim nos valores", () => {
    const { errors, values } = validateItem({
      name: "  Notebook  ",
      description: "  14 polegadas  ",
    });
    expect(Object.keys(errors)).toHaveLength(0);
    expect(values.name).toBe("Notebook");
    expect(values.description).toBe("14 polegadas");
  });

  it("aceita descrição vazia", () => {
    const { errors, values } = validateItem({ name: "Item", description: "" });
    expect(Object.keys(errors)).toHaveLength(0);
    expect(values.description).toBe("");
  });
});
