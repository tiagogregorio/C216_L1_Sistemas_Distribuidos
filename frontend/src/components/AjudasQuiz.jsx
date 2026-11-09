import { useState } from "react";
import { assistenteIA } from "../services/api";
import { useSound } from "../sound/SoundContext";

/**
 * Simula a "ajuda da plateia": gera uma distribuicao de votos em que a
 * alternativa correta sempre aparece como a mais votada (pelo menos 60%),
 * funcionando como uma dica confiavel para quem esta estudando.
 */
function gerarEstatisticasSimuladas(respostaCorreta) {
	const letras = ["A", "B", "C", "D", "E"];
	const porAlternativa = {};

	// Primeiro passo: reserva a posicao de cada letra, nesta ordem (A-E),
	// para que o objeto resultante sempre itere nessa mesma ordem — em JS,
	// a ordem de um objeto segue a ordem em que cada chave foi inserida
	// pela primeira vez, entao definir todas aqui evita que a alternativa
	// correta "pule" para o final quando for preenchida depois.
	for (const letra of letras) {
		porAlternativa[letra] = 0;
	}

	let somaErradas = 0;
	for (const letra of letras) {
		if (letra !== respostaCorreta) {
			const pct = Math.floor(Math.random() * 11); // 0 a 10% cada errada
			porAlternativa[letra] = pct;
			somaErradas += pct;
		}
	}
	porAlternativa[respostaCorreta] = 100 - somaErradas; // sempre a maior

	return {
		totalUniversitarios: 30 + Math.floor(Math.random() * 170),
		porAlternativa,
		maisEscolhida: respostaCorreta,
	};
}

export default function AjudasQuiz({
	questaoId,
	respostaCorreta,
	confirmada,
	cartasUsada,
	onUsarCartas,
	universitariosUsada,
	onUsarUniversitarios,
	iaUsada,
	onUsarIA,
}) {
	const [estatisticas, setEstatisticas] = useState(null);
	const [explicacaoIA, setExplicacaoIA] = useState(null);
	const [carregandoIA, setCarregandoIA] = useState(false);
	const [erroIA, setErroIA] = useState(null);
	const { playHelp } = useSound();

	function usarCartas() {
		if (cartasUsada || confirmada) return;
		playHelp();
		onUsarCartas();
	}

	function usarUniversitarios() {
		if (universitariosUsada || confirmada) return;
		playHelp();
		onUsarUniversitarios();
		setEstatisticas(gerarEstatisticasSimuladas(respostaCorreta));
	}

	async function usarIA() {
		if (iaUsada || confirmada) return;
		playHelp();
		onUsarIA();
		setCarregandoIA(true);
		setErroIA(null);
		try {
			const resultado = await assistenteIA(questaoId);
			setExplicacaoIA(resultado.explicacao);
		} catch (err) {
			setErroIA(err.message);
		} finally {
			setCarregandoIA(false);
		}
	}

	return (
		<div className="mb-5">
			<div className="flex gap-3">
				<button
					type="button"
					onClick={usarCartas}
					disabled={cartasUsada || confirmada}
					title="Elimina de uma a quatro alternativas erradas"
					className="flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-purple-400/40 bg-purple-900/30 text-purple-200 text-sm font-bold hover:bg-purple-800/40 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
				>
					<svg
						viewBox="0 0 24 24"
						className="w-5 h-5"
						fill="none"
						stroke="currentColor"
						strokeWidth="1.8"
						aria-hidden="true"
					>
						<rect x="3" y="7" width="13" height="14" rx="2" />
						<rect x="7" y="3" width="13" height="14" rx="2" />
					</svg>
					Cartas
				</button>

				<button
					type="button"
					onClick={usarUniversitarios}
					disabled={universitariosUsada || confirmada}
					title="Mostra como os universitarios responderam"
					className="flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-cyan-400/40 bg-cyan-900/30 text-cyan-200 text-sm font-bold hover:bg-cyan-800/40 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
				>
					<svg
						viewBox="0 0 24 24"
						className="w-5 h-5"
						fill="none"
						stroke="currentColor"
						strokeWidth="1.8"
						aria-hidden="true"
					>
						<circle cx="9" cy="8" r="3" />
						<path d="M3 20c0-3 3-5 6-5s6 2 6 5" />
						<circle cx="17" cy="9" r="2.3" />
						<path d="M15.5 20c.2-2.3 1.8-4 3.8-4.4" />
					</svg>
					Universitarios
				</button>

				<button
					type="button"
					onClick={usarIA}
					disabled={iaUsada || confirmada}
					title="Pede uma explicacao ao assistente de IA"
					className="flex items-center gap-2 px-4 py-2 rounded-lg border-2 border-emerald-400/40 bg-emerald-900/30 text-emerald-200 text-sm font-bold hover:bg-emerald-800/40 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
				>
					<svg
						viewBox="0 0 24 24"
						className="w-5 h-5"
						fill="none"
						stroke="currentColor"
						strokeWidth="1.8"
						aria-hidden="true"
					>
						<rect x="4" y="7" width="16" height="12" rx="3" />
						<circle cx="9" cy="13" r="1.3" fill="currentColor" stroke="none" />
						<circle cx="15" cy="13" r="1.3" fill="currentColor" stroke="none" />
						<path d="M12 7V4" strokeLinecap="round" />
						<circle cx="12" cy="3" r="1" fill="currentColor" stroke="none" />
					</svg>
					Assistente IA
				</button>
			</div>

			{iaUsada && (
				<div className="mt-3 bg-emerald-950/50 border border-emerald-500/30 rounded-xl p-4 text-sm">
					{carregandoIA && (
						<p className="text-emerald-300">
							Consultando o assistente de IA...
						</p>
					)}
					{erroIA && <p className="text-amber-300">{erroIA}</p>}
					{explicacaoIA && (
						<p className="text-emerald-100 whitespace-pre-line">
							{explicacaoIA}
						</p>
					)}
				</div>
			)}

			{universitariosUsada && estatisticas && (
				<div className="mt-3 bg-cyan-950/50 border border-cyan-500/30 rounded-xl p-4 text-sm">
					<p className="text-cyan-200 mb-3">
						{estatisticas.totalUniversitarios} universitario(s) responderam esta
						questao. A mais escolhida foi a alternativa{" "}
						<strong>{estatisticas.maisEscolhida}</strong>.
					</p>
					<div className="flex gap-2">
						{Object.entries(estatisticas.porAlternativa).map(([letra, pct]) => {
							const destaque = letra === estatisticas.maisEscolhida;
							return (
								<div key={letra} className="flex-1 text-center">
									<div
										className="h-16 bg-black/30 rounded flex items-end overflow-hidden"
										title={`${letra}: ${pct}%`}
									>
										<div
											className={
												destaque
													? "w-full bg-gradient-to-t from-amber-500 via-yellow-400 to-amber-300"
													: "w-full bg-cyan-400/70"
											}
											style={{ height: `${pct}%` }}
										/>
									</div>
									<div
										className={
											destaque
												? "text-xs mt-1 font-black bg-gradient-to-r from-amber-400 to-yellow-300 bg-clip-text text-transparent"
												: "text-xs text-cyan-300 mt-1"
										}
									>
										{letra} · {pct}%
									</div>
								</div>
							);
						})}
					</div>
				</div>
			)}
		</div>
	);
}
