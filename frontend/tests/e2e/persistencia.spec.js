import { expect, test } from "@playwright/test";

// Endereco da API usado para conferir o banco por fora da interface.
const API_URL = process.env.E2E_API_URL || "http://localhost:8000";

test.describe("Persistencia real: frontend -> API -> PostgreSQL", () => {
	test("cadastra, edita e remove uma questao, e tudo persiste no banco", async ({
		page,
		request,
	}) => {
		// Marca unica para identificar a questao deste teste.
		const marca = `E2E-${Date.now()}`;
		const numero = 5000 + Math.floor(Math.random() * 4000);

		await page.goto("/");
		await page.getByRole("button", { name: "Questoes" }).click();
		await expect(page.getByText("Banco de Questoes")).toBeVisible();

		// 1. Cadastro pela interface.
		await page.getByRole("button", { name: "+ Nova Questao" }).click();
		const form = page.locator("form");
		await form.locator('input[type="number"]').nth(0).fill("2024");
		await form.locator('input[type="number"]').nth(1).fill(String(numero));
		await form.getByPlaceholder("Ex: Algoritmos de Ordenacao").fill(marca);
		await form
			.getByPlaceholder("Texto completo da questao...")
			.fill("Enunciado de teste automatizado do Playwright.");
		const alternativas = form.locator('input[type="text"]');
		const total = await alternativas.count();
		// As 5 ultimas entradas de texto sao as alternativas A a E.
		for (let i = 0; i < 5; i++) {
			await alternativas.nth(total - 5 + i).fill(`Alternativa ${i + 1}`);
		}
		await form.getByRole("button", { name: "Cadastrar Questao" }).click();

		// 2. A questao aparece na lista.
		await expect(page.getByText(marca)).toBeVisible();

		// 3. Persistencia: recarrega a pagina e consulta direto a API.
		await page.reload();
		await page.getByRole("button", { name: "Questoes" }).click();
		await expect(page.getByText(marca)).toBeVisible();

		const resposta = await request.get(`${API_URL}/questoes/?ano=2024`);
		expect(resposta.ok()).toBeTruthy();
		const questoes = await resposta.json();
		expect(questoes.some((q) => q.assunto === marca)).toBeTruthy();

		// 4. Edicao pela interface: troca o assunto e salva.
		const editada = `${marca}-editada`;
		await page
			.locator("div.rounded-xl", { hasText: marca })
			.getByRole("button", { name: "Editar" })
			.click();
		await expect(page.getByText(/Editar Questao/)).toBeVisible();
		await page.getByPlaceholder("Ex: Algoritmos de Ordenacao").fill(editada);
		await page.getByRole("button", { name: "Atualizar Questao" }).click();
		await expect(page.getByText(editada)).toBeVisible();

		// A edicao tambem foi para o banco (conferido pela API).
		const aposEditar = await (
			await request.get(`${API_URL}/questoes/?ano=2024`)
		).json();
		expect(aposEditar.some((q) => q.assunto === editada)).toBeTruthy();

		// 5. Exclusao pela interface (aceita o confirm do navegador).
		page.once("dialog", (dialog) => dialog.accept());
		await page
			.locator("div.rounded-xl", { hasText: editada })
			.getByRole("button", { name: "Remover" })
			.click();
		await expect(page.getByText(editada)).toHaveCount(0);

		// 6. A exclusao tambem foi para o banco.
		const depois = await request.get(`${API_URL}/questoes/?ano=2024`);
		const restantes = await depois.json();
		expect(restantes.some((q) => q.assunto === editada)).toBeFalsy();
	});
});
