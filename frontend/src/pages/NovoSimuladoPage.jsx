import { useEffect, useState } from "react";
import {
	coberturaQuestoes,
	criarSimulado,
	reiniciarCobertura,
} from "../services/api";
import { validarSimulado } from "../validation";

export default function NovoSimuladoPage({ onIniciar }) {
	const [dados, setDados] = useState({
		nome: "",
		quantidade: 10,
		ano: "",
		tipo: "",
		dificuldade: "",
		modo: "aleatorio",
	});
	const [erros, setErros] = useState({});
	const [enviando, setEnviando] = useState(false);
	const [cobertura, setCobertura] = useState(null);
	const [reiniciando, setReiniciando] = useState(false);

	useEffect(() => {
		if (dados.modo !== "sem_repetir") return;
		coberturaQuestoes()
			.then(setCobertura)
			.catch(() => setCobertura(null));
	}, [dados.modo]);

	async function handleReiniciarCobertura() {
		if (
			!confirm(
				"Comecar um novo ciclo? Voce podera responder todas as questoes " +
					"de novo no modo sem repetir. Seu historico e dashboard nao " +
					"serao apagados.",
			)
		) {
			return;
		}
		setReiniciando(true);
		try {
			const nova = await reiniciarCobertura();
			setCobertura(nova);
		} catch (err) {
			setErros({ geral: err.message });
		} finally {
			setReiniciando(false);
		}
	}

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
			payload.modo = dados.modo;

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

				<div>
					<label className="block text-sm mb-2 text-gray-300">
						Modo do simulado
					</label>
					<div className="grid grid-cols-2 gap-3">
						<button
							type="button"
							onClick={() => handleChange("modo", "aleatorio")}
							className={`text-left px-4 py-3 rounded-lg border-2 transition-colors cursor-pointer ${
								dados.modo === "aleatorio"
									? "border-[var(--cor-destaque)] bg-[var(--cor-destaque)]/10"
									: "border-[var(--cor-borda)] hover:border-gray-500"
							}`}
						>
							<div className="font-bold text-sm">Aleatorio</div>
							<div className="text-xs text-gray-400 mt-0.5">
								Qualquer questao pode cair, mesmo repetida
							</div>
						</button>
						<button
							type="button"
							onClick={() => handleChange("modo", "sem_repetir")}
							className={`text-left px-4 py-3 rounded-lg border-2 transition-colors cursor-pointer ${
								dados.modo === "sem_repetir"
									? "border-[var(--cor-destaque)] bg-[var(--cor-destaque)]/10"
									: "border-[var(--cor-borda)] hover:border-gray-500"
							}`}
						>
							<div className="font-bold text-sm">Sem repetir</div>
							<div className="text-xs text-gray-400 mt-0.5">
								Cobre o banco inteiro sem repetir questao
							</div>
						</button>
					</div>

					{dados.modo === "sem_repetir" && cobertura && (
						<div className="mt-3">
							<div className="flex items-center justify-between text-xs text-gray-400 mb-1">
								<span>
									{cobertura.respondidas} de {cobertura.total} questoes ja
									cobertas
								</span>
								<span className="font-bold text-[var(--cor-destaque)]">
									{cobertura.percentual}%
								</span>
							</div>
							<div className="bg-[var(--cor-fundo)] rounded-full h-2 overflow-hidden">
								<div
									className="h-full bg-[var(--cor-destaque)] transition-all"
									style={{ width: `${cobertura.percentual}%` }}
								/>
							</div>
							{cobertura.percentual >= 100 && (
								<div className="mt-2">
									<p className="text-xs text-[var(--cor-acerto)] font-bold">
										Parabens! Voce ja cobriu 100% das questoes do banco.
									</p>
									<button
										type="button"
										onClick={handleReiniciarCobertura}
										disabled={reiniciando}
										className="mt-2 text-xs font-bold text-[var(--cor-destaque)] underline cursor-pointer disabled:opacity-50"
									>
										{reiniciando
											? "Reiniciando..."
											: "Reiniciar cobertura e treinar de novo"}
									</button>
								</div>
							)}
						</div>
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
