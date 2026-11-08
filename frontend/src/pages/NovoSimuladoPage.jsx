import { useState } from "react";
import { criarSimulado } from "../services/api";
import { validarSimulado } from "../validation";

export default function NovoSimuladoPage({ onIniciar }) {
	const [dados, setDados] = useState({
		nome: "",
		quantidade: 10,
		ano: "",
		tipo: "",
		dificuldade: "",
	});
	const [erros, setErros] = useState({});
	const [enviando, setEnviando] = useState(false);

	function handleChange(campo, valor) {
		setDados((prev) => ({ ...prev, [campo]: valor }));
	}

	async function handleSubmit(e) {
		e.preventDefault();
		const validacao = validarSimulado(dados);
		if (Object.keys(validacao).length > 0) {
			setErros(validacao);
			return;
		}

		setEnviando(true);
		setErros({});
		try {
			const payload = {
				nome: dados.nome,
				quantidade: Number(dados.quantidade),
			};
			if (dados.ano) payload.ano = Number(dados.ano);
			if (dados.tipo) payload.tipo = dados.tipo;
			if (dados.dificuldade) payload.dificuldade = dados.dificuldade;

			const resultado = await criarSimulado(payload);
			onIniciar(resultado.simulado.id, resultado.questao_ids);
		} catch (err) {
			setErros({ geral: err.message });
		} finally {
			setEnviando(false);
		}
	}

	const inputClass =
		"w-full bg-[var(--cor-fundo)] border border-[var(--cor-borda)] rounded-lg px-4 py-3 text-[var(--cor-texto)] focus:border-[var(--cor-destaque)] focus:outline-none text-lg";

	return (
		<div className="max-w-2xl mx-auto p-6">
			<div className="text-center mb-8">
				<h1 className="text-3xl font-bold text-[var(--cor-destaque)] mb-2">
					Novo Simulado
				</h1>
				<p className="text-gray-400">Configure as opcoes e inicie sua prova</p>
			</div>

			<form
				onSubmit={handleSubmit}
				className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-2xl p-8 space-y-6"
			>
				{erros.geral && (
					<div
						role="alert"
						className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg"
					>
						{erros.geral}
					</div>
				)}

				<div>
					<label className="block text-sm mb-2 text-gray-300">
						Nome do simulado
					</label>
					<input
						type="text"
						value={dados.nome}
						onChange={(e) => handleChange("nome", e.target.value)}
						className={inputClass}
						placeholder="Ex: Revisao ENADE 2019"
					/>
					{erros.nome && (
						<p className="text-red-400 text-sm mt-1">{erros.nome}</p>
					)}
				</div>

				<div>
					<label className="block text-sm mb-2 text-gray-300">
						Quantidade de questoes
					</label>
					<input
						type="number"
						value={dados.quantidade}
						onChange={(e) => handleChange("quantidade", e.target.value)}
						className={inputClass}
						min="1"
						max="50"
					/>
					{erros.quantidade && (
						<p className="text-red-400 text-sm mt-1">{erros.quantidade}</p>
					)}
				</div>

				<div className="grid grid-cols-3 gap-4">
					<div>
						<label className="block text-sm mb-2 text-gray-300">
							Ano (opcional)
						</label>
						<select
							value={dados.ano}
							onChange={(e) => handleChange("ano", e.target.value)}
							className={inputClass}
						>
							<option value="">Todos</option>
							<option value="2014">2014</option>
							<option value="2017">2017</option>
							<option value="2019">2019</option>
							<option value="2023">2023</option>
						</select>
					</div>
					<div>
						<label className="block text-sm mb-2 text-gray-300">
							Tipo (opcional)
						</label>
						<select
							value={dados.tipo}
							onChange={(e) => handleChange("tipo", e.target.value)}
							className={inputClass}
						>
							<option value="">Todos</option>
							<option value="CE">Comp. Especifico</option>
							<option value="FG">Form. Geral</option>
						</select>
					</div>
					<div>
						<label className="block text-sm mb-2 text-gray-300">
							Dificuldade
						</label>
						<select
							value={dados.dificuldade}
							onChange={(e) => handleChange("dificuldade", e.target.value)}
							className={inputClass}
						>
							<option value="">Todas</option>
							<option value="facil">Facil</option>
							<option value="medio">Medio</option>
							<option value="dificil">Dificil</option>
						</select>
					</div>
				</div>

				<button
					type="submit"
					disabled={enviando}
					className="w-full bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold py-4 rounded-xl text-xl hover:brightness-110 transition disabled:opacity-50 cursor-pointer"
				>
					{enviando ? "Gerando simulado..." : "Iniciar Simulado"}
				</button>
			</form>
		</div>
	);
}
