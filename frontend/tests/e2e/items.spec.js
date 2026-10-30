import { expect, test } from "@playwright/test";

test.describe("Gerenciador de Itens", () => {
  test("carrega a interface corretamente", async ({ page }) => {
    await page.goto("/");

    await expect(
      page.getByRole("heading", { name: "Gerenciador de Itens" }),
    ).toBeVisible();
    await expect(page.getByText("Nenhum item cadastrado.")).toBeVisible();
    await expect(page.getByRole("button", { name: "Adicionar" })).toBeVisible();
  });

  test("cadastra um item e o exibe na listagem", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("Nome").fill("Notebook");
    await page.getByLabel("Descrição").fill("14 polegadas");
    await page.getByRole("button", { name: "Adicionar" }).click();

    await expect(page.getByRole("listitem")).toContainText("Notebook");
    await expect(page.getByText("Nenhum item cadastrado.")).toBeHidden();
  });

  test("mostra erro de validação com nome vazio", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Adicionar" }).click();

    await expect(page.getByRole("alert")).toContainText(
      "O nome é obrigatório.",
    );
  });
});
