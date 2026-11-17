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

	test("cria simulado, responde e navega entre questoes ate finalizar", async ({
		page,
	}) => {
		await page.goto("/");
		await page.getByRole("button", { name: "Novo Simulado" }).click();

		await page.getByPlaceholder("Ex: Revisao ENADE 2019").fill("E2E Test");
		await page.getByRole("spinbutton").fill("5");
		await page.getByRole("button", { name: "Iniciar Simulado" }).click();

		// O simulado foi criado pela API e a primeira questao esta na tela.
		await expect(page.getByText("Pergunta 1 de 5")).toBeVisible();

		for (let i = 0; i < 5; i++) {
			await expect(page.getByText(`Pergunta ${i + 1} de 5`)).toBeVisible();
			await page.locator("button:has-text('1')").first().click();
			await page.getByRole("button", { name: "CONFIRMAR RESPOSTA" }).click();
			await expect(page.getByText(/RESPOSTA CERTA|ERROU/)).toBeVisible();
			// Depois de confirmar, a aplicacao avanca sozinha para a proxima.
		}

		await page.getByRole("button", { name: "Finalizar" }).click();

		await expect(page.getByText("Resultado")).toBeVisible();
		await expect(page.getByText("Voltar ao Menu")).toBeVisible();
	});

	test("permite voltar para revisar uma questao ja respondida", async ({
		page,
	}) => {
		await page.goto("/");
		await page.getByRole("button", { name: "Novo Simulado" }).click();

		await page.getByPlaceholder("Ex: Revisao ENADE 2019").fill("E2E Revisao");
		await page.getByRole("spinbutton").fill("3");
		await page.getByRole("button", { name: "Iniciar Simulado" }).click();
		await expect(page.getByText("Pergunta 1 de 3")).toBeVisible();

		// Responde a primeira questao; a aplicacao avanca sozinha.
		await page.locator("button:has-text('1')").first().click();
		await page.getByRole("button", { name: "CONFIRMAR RESPOSTA" }).click();

		await expect(page.getByText("Pergunta 2 de 3")).toBeVisible();

		// Volta e deve ver a primeira questao em modo revisao (sem o botao
		// de confirmar, ja que a resposta foi preservada).
		await page.getByRole("button", { name: "◀ Voltar" }).click();
		await expect(page.getByText("Pergunta 1 de 3")).toBeVisible();
		await expect(page.getByText("Revisao")).toBeVisible();
		await expect(
			page.getByRole("button", { name: "CONFIRMAR RESPOSTA" }),
		).toHaveCount(0);
	});
});
