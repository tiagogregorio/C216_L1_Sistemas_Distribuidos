import { expect, test } from "@playwright/test";

test.describe("Gerenciador de Tarefas — E2E", () => {
  test("carrega a interface corretamente", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByRole("heading", { name: "Gerenciador de Tarefas" }),
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Adicionar" })).toBeVisible();
  });

  test("cria uma tarefa e persiste após recarregar", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("Título").fill("Tarefa E2E");
    await page.getByRole("button", { name: "Adicionar" }).click();

    await expect(page.getByText("Tarefa E2E")).toBeVisible();

    await page.reload();
    await expect(page.getByText("Tarefa E2E")).toBeVisible();
  });

  test("conclui e reabre uma tarefa", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("Título").fill("Tarefa Toggle");
    await page.getByRole("button", { name: "Adicionar" }).click();
    await expect(page.getByText("Tarefa Toggle")).toBeVisible();

    await page.getByRole("button", { name: "Concluir" }).first().click();
    await expect(
      page.getByRole("button", { name: "Reabrir" }).first(),
    ).toBeVisible();

    await page.getByRole("button", { name: "Reabrir" }).first().click();
    await expect(
      page.getByRole("button", { name: "Concluir" }).first(),
    ).toBeVisible();
  });

  test("exclui uma tarefa", async ({ page }) => {
    await page.goto("/");

    await page.getByLabel("Título").fill("Tarefa Excluir");
    await page.getByRole("button", { name: "Adicionar" }).click();
    await expect(page.getByText("Tarefa Excluir")).toBeVisible();

    await page.getByRole("button", { name: "Excluir" }).first().click();
    await expect(page.getByText("Tarefa Excluir")).toBeHidden();
  });

  test("mostra erro de validação com título vazio", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Adicionar" }).click();
    await expect(page.getByRole("alert")).toContainText(
      "O título é obrigatório.",
    );
  });
});
