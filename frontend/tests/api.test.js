import { afterEach, describe, expect, it, vi } from "vitest";
import { criarQuestao, statusIA } from "../src/services/api";

afterEach(() => vi.unstubAllGlobals());

function respostaHttp(status, corpo) {
	return { ok: status < 400, status, json: async () => corpo };
}

describe("api - erros", () => {
	it("troca 'NetworkError' por uma mensagem que diz o que fazer", async () => {
		vi.stubGlobal(
			"fetch",
			vi
				.fn()
				.mockRejectedValue(
					new TypeError("NetworkError when attempting to fetch resource."),
				),
		);
		await expect(statusIA()).rejects.toMatchObject({
			rede: true,
			message: expect.stringContaining("docker compose logs backend"),
		});
	});

	it("mostra o detalhe de um erro 500 devolvido pelo servidor", async () => {
		vi.stubGlobal(
			"fetch",
			vi
				.fn()
				.mockResolvedValue(
					respostaHttp(500, { detail: "Erro interno (ProgrammingError)" }),
				),
		);
		await expect(criarQuestao({})).rejects.toMatchObject({
			status: 500,
			message: expect.stringContaining("ProgrammingError"),
		});
	});

	it("junta as mensagens de validacao 422", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue(
				respostaHttp(422, {
					detail: [{ msg: "campo A" }, { msg: "campo B" }],
				}),
			),
		);
		await expect(criarQuestao({})).rejects.toMatchObject({
			status: 422,
			message: "campo A; campo B",
		});
	});

	it("nao quebra quando o erro vem sem JSON (ex.: 502 do proxy)", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue({
				ok: false,
				status: 502,
				json: async () => {
					throw new SyntaxError("nao e json");
				},
			}),
		);
		await expect(statusIA()).rejects.toMatchObject({
			status: 502,
			message: expect.stringContaining("HTTP 502"),
		});
	});
});
