import { expect, test } from "@playwright/test";

test.describe("Fluxo completo da plataforma ENADE", () => {
	test("navega entre as paginas", async ({ page }) => {
		await page.goto("/");

		await expect(page.getByText("Dashboard de Desempenho")).toBeVisible();

		await page.getByRole("button", { name: "Questoes" }).click();
		await expect(page.getByText("Banco de Questoes")).toBeVisible();

		await page.getByRole("button", { name: "Novo Simulado" }).click();
		await expect(
			page.getByText("Configure as opcoes e inicie sua prova"),
		).toBeVisible();

		await page.getByRole("button", { name: "Historico" }).click();
		await expect(page.getByText("Historico de Simulados")).toBeVisible();
	});

	test("lista questoes do banco", async ({ page }) => {
		await page.goto("/");
		await page.getByRole("button", { name: "Questoes" }).click();

		await page.waitForSelector('[class*="rounded-xl"]', { timeout: 5000 });

		const questoes = page.locator("text=Comp. Especifico");
		await expect(questoes.first()).toBeVisible();
	});

	test("cria simulado e responde questoes", async ({ page }) => {
		await page.goto("/");
		await page.getByRole("button", { name: "Novo Simulado" }).click();

		await page.getByPlaceholder("Ex: Revisao ENADE 2019").fill("E2E Test");
		await page.getByRole("spinbutton").fill("5");
		await page.getByRole("button", { name: "Iniciar Simulado" }).click();

		await page.waitForSelector("text=ENADE", { timeout: 5000 });

		for (let i = 0; i < 5; i++) {
			await page.locator("button:has-text('1')").first().click();
			await page.getByRole("button", { name: "CONFIRMAR RESPOSTA" }).click();
			await page.waitForTimeout(2500);
		}

		await expect(page.getByText("Resultado")).toBeVisible();
		await expect(page.getByText("Voltar ao Menu")).toBeVisible();
	});
});
