import { defineConfig } from "@playwright/test";

// Os testes E2E rodam contra a aplicacao REAL (frontend + API + PostgreSQL),
// normalmente a subida pelo Docker Compose: frontend em localhost:3000.
// Para apontar para outro endereco: E2E_BASE_URL=http://localhost:5173
export default defineConfig({
	testDir: "./tests/e2e",
	timeout: 30000,
	use: {
		baseURL: process.env.E2E_BASE_URL || "http://localhost:3000",
		headless: true,
	},
});
