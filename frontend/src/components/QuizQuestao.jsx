import { useEffect, useState } from "react";
import { useSound } from "../sound/SoundContext";
import AjudasQuiz from "./AjudasQuiz";

export default function QuizQuestao({
	questao,
	numero,
	total,
	respostaSalva,
	respondidas,
	onResponder,
}) {
	const [selecionada, setSelecionada] = useState(
		respostaSalva?.alternativa_escolhida ?? null,
	);
	const [confirmada, setConfirmada] = useState(Boolean(respostaSalva));
	const [tempo, setTempo] = useState(respostaSalva?.tempo_resposta ?? 0);
	const [eliminadas, setEliminadas] = useState([]);
	const [cartasUsada, setCartasUsada] = useState(false);
	const [universitariosUsada, setUniversitariosUsada] = useState(false);
	const [iaUsada, setIaUsada] = useState(false);
	const [mostrarPdf, setMostrarPdf] = useState(false);
	const { playSelect, playCorrect, playWrong } = useSound();

	// Troca de questao (inclusive ao navegar com Voltar/Avancar): se ja houver
	// resposta salva para ela, mostra em modo revisao; senao, comeca em branco.
	useEffect(() => {
		setSelecionada(respostaSalva?.alternativa_escolhida ?? null);
		setConfirmada(Boolean(respostaSalva));
		setTempo(respostaSalva?.tempo_resposta ?? 0);
		setEliminadas([]);
		setCartasUsada(false);
		setUniversitariosUsada(false);
		setIaUsada(false);
		setMostrarPdf(false);
	}, [questao.id]);

	useEffect(() => {
		if (confirmada) return;
		const timer = setInterval(() => setTempo((t) => t + 1), 1000);
		return () => clearInterval(timer);
	}, [confirmada, questao.id]);

	// Esc fecha a pagina original do PDF.
	useEffect(() => {
		if (!mostrarPdf) return;
		function aoTeclar(e) {
			if (e.key === "Escape") setMostrarPdf(false);
		}
		document.addEventListener("keydown", aoTeclar);
		return () => document.removeEventListener("keydown", aoTeclar);
	}, [mostrarPdf]);

	function selecionar(letra) {
		if (confirmada || eliminadas.includes(letra)) return;
		setSelecionada(letra);
		playSelect();
	}

	function usarCartas() {
		const erradas = ["A", "B", "C", "D", "E"].filter(
			(letra) => letra !== questao.resposta,
		);
		// Elimina uma quantidade aleatoria de alternativas erradas (1 a 4).
		const quantidade = 1 + Math.floor(Math.random() * erradas.length);
		const embaralhadas = [...erradas].sort(() => Math.random() - 0.5);
		const escolhidas = embaralhadas.slice(0, quantidade);
		setEliminadas(escolhidas);
		setCartasUsada(true);
		if (escolhidas.includes(selecionada)) {
			setSelecionada(null);
		}
	}

	function confirmar() {
		if (!selecionada) return;
		setConfirmada(true);
		const correta = selecionada === questao.resposta;
		if (correta) {
			playCorrect();
		} else {
			playWrong();
		}
		onResponder({
			questao_id: questao.id,
			alternativa_escolhida: selecionada,
			tempo_resposta: tempo,
			correta,
		});
	}

	function formatarTempo(s) {
		const min = Math.floor(s / 60);
		const seg = s % 60;
		return `${min.toString().padStart(2, "0")}:${seg.toString().padStart(2, "0")}`;
	}

	function estiloBotao(letra) {
		if (!confirmada) {
			if (eliminadas.includes(letra)) {
				return "bg-gray-900/40 text-gray-600 border-gray-700/30 opacity-40 line-through cursor-not-allowed";
			}
			if (selecionada === letra) {
				return "bg-gradient-to-r from-yellow-500 to-amber-400 text-gray-900 border-yellow-300 scale-[1.02] shadow-lg shadow-yellow-500/30";
			}
			return "bg-gradient-to-r from-blue-700 to-blue-600 hover:from-blue-600 hover:to-blue-500 text-white border-blue-400/50 hover:border-blue-300";
		}
		if (letra === questao.resposta) {
			return "bg-gradient-to-r from-green-600 to-green-500 text-white border-green-300 animate-pulse shadow-lg shadow-green-500/40";
		}
		if (letra === selecionada && selecionada !== questao.resposta) {
			return "bg-gradient-to-r from-red-700 to-red-600 text-white border-red-400";
		}
		return "bg-gradient-to-r from-blue-900 to-blue-800 text-gray-400 border-blue-700/30 opacity-50";
	}

	const alternativas = [
		{ letra: "A", num: 1, texto: questao.alternativa_a },
		{ letra: "B", num: 2, texto: questao.alternativa_b },
		{ letra: "C", num: 3, texto: questao.alternativa_c },
		{ letra: "D", num: 4, texto: questao.alternativa_d },
		{ letra: "E", num: 5, texto: questao.alternativa_e },
	];

	return (
		<div className="max-w-4xl mx-auto px-4">
			{mostrarPdf && questao.pagina_original && (
				<dialog
					open
					aria-label="Pagina original da prova em PDF"
					className="fixed inset-0 z-50 m-0 h-full w-full max-w-none overflow-auto bg-black/85 p-4 text-inherit"
				>
					<div className="max-w-3xl mx-auto">
						<button
							type="button"
							onClick={() => setMostrarPdf(false)}
							className="sticky top-2 ml-auto block mb-3 bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold px-4 py-1.5 rounded-lg cursor-pointer"
						>
							Fechar (Esc)
						</button>
						<img
							src={questao.pagina_original}
							alt="Pagina original da prova em PDF"
							className="w-full rounded-lg bg-white"
						/>
					</div>
				</dialog>
			)}

			{/* Header com progresso e timer */}
			<div className="flex items-center justify-between mb-4">
				<div className="flex items-center gap-3">
					{questao.dificuldade && (
						<span
							className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${
								questao.dificuldade === "facil"
									? "bg-green-500/20 text-green-300 border border-green-500/40"
									: questao.dificuldade === "medio"
										? "bg-yellow-500/20 text-yellow-300 border border-yellow-500/40"
										: "bg-red-500/20 text-red-300 border border-red-500/40"
							}`}
						>
							{questao.dificuldade}
						</span>
					)}
					{questao.assunto && (
						<span className="text-xs text-cyan-300/60">{questao.assunto}</span>
					)}
				</div>
				<div className="bg-black/40 border border-cyan-500/30 rounded-xl px-5 py-2 font-mono">
					<span className="text-cyan-400 text-2xl font-bold">
						{formatarTempo(tempo)}
					</span>
				</div>
			</div>

			{/* Barra de progresso: verde = respondida, amarelo = atual, cinza = pendente */}
			<div className="flex items-center gap-2 mb-6">
				{Array.from({ length: total }, (_, i) => (
					<div
						key={`passo-${i}-de-${total}`}
						title={`Pergunta ${i + 1}${respondidas?.[i] ? " (respondida)" : ""}`}
						className={`h-2 flex-1 rounded-full transition-all duration-300 ${
							i === numero - 1
								? "bg-yellow-400"
								: respondidas?.[i]
									? "bg-gradient-to-r from-green-400 to-cyan-400"
									: "bg-gray-700"
						}`}
					/>
				))}
			</div>

			{/* Enunciado - estilo tela do show */}
			<div className="relative mb-6">
				<div className="bg-gradient-to-r from-cyan-900/80 via-teal-800/80 to-cyan-900/80 border-2 border-cyan-400/40 rounded-2xl p-6 shadow-xl shadow-cyan-500/10">
					<div className="flex items-center gap-3 mb-3">
						<span className="bg-gradient-to-r from-yellow-400 to-amber-500 text-gray-900 font-black text-sm px-4 py-1 rounded-full">
							{questao.fonte || `ENADE ${questao.ano}`}
						</span>
						<span className="text-cyan-300/70 text-sm font-medium">
							Questao {questao.numero} | Pergunta {numero} de {total}
						</span>
						{confirmada && (
							<span className="text-xs bg-black/30 text-cyan-200 px-2 py-0.5 rounded-full">
								Revisao
							</span>
						)}
						<button
							type="button"
							onClick={() => setMostrarPdf(true)}
							disabled={!questao.pagina_original}
							title={
								questao.pagina_original
									? "Abre a pagina original da prova em PDF"
									: "Esta questao nao tem a pagina do PDF anexada. Reimporte o PDF em Questoes > Importar PDF para anexar."
							}
							className="ml-auto flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-lg border border-cyan-300/40 text-cyan-100 bg-black/20 hover:bg-black/40 transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
						>
							<svg
								viewBox="0 0 24 24"
								className="w-4 h-4"
								fill="none"
								stroke="currentColor"
								strokeWidth="1.8"
								aria-hidden="true"
							>
								<path d="M7 3h7l5 5v13H7z" />
								<path d="M14 3v5h5" />
								<path d="M10 13h6M10 17h6" />
							</svg>
							Ver pagina do PDF
						</button>
					</div>
					<p className="text-white text-lg leading-relaxed whitespace-pre-line font-medium">
						{questao.enunciado}
					</p>
					{questao.imagem && (
						<img
							src={questao.imagem}
							alt="Codigo, diagrama ou tabela de apoio desta questao"
							className="mt-4 max-w-full rounded-lg border border-cyan-400/30"
						/>
					)}
				</div>
			</div>

			{/* Ajudas estilo show de perguntas */}
			<AjudasQuiz
				questaoId={questao.id}
				respostaCorreta={questao.resposta}
				confirmada={confirmada}
				cartasUsada={cartasUsada}
				onUsarCartas={usarCartas}
				universitariosUsada={universitariosUsada}
				onUsarUniversitarios={() => setUniversitariosUsada(true)}
				iaUsada={iaUsada}
				onUsarIA={() => setIaUsada(true)}
			/>

			{/* Alternativas - estilo Show do Milhão */}
			<div className="space-y-3 mb-6">
				{alternativas.map(({ letra, num, texto }) => (
					<button
						key={letra}
						type="button"
						onClick={() => selecionar(letra)}
						disabled={confirmada || eliminadas.includes(letra)}
						className={`w-full text-left rounded-xl border-2 transition-all duration-300 cursor-pointer flex items-center overflow-hidden ${estiloBotao(letra)}`}
					>
						<div className="bg-black/30 flex items-center justify-center w-14 h-full min-h-[56px] border-r border-white/10">
							<span
								className={`flex items-center justify-center w-9 h-9 rounded-full text-2xl font-black ${
									selecionada === letra && !confirmada ? "luz-girando" : ""
								}`}
							>
								{num}
							</span>
						</div>
						<div className="px-5 py-3 flex-1">
							<span className="text-base font-medium">{texto}</span>
						</div>
					</button>
				))}
			</div>

			{/* Botão confirmar */}
			{!confirmada && (
				<button
					type="button"
					onClick={confirmar}
					disabled={!selecionada}
					className="w-full bg-gradient-to-r from-green-600 to-emerald-500 text-white font-black py-4 rounded-xl text-xl hover:from-green-500 hover:to-emerald-400 transition-all disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer border-2 border-green-300/30 shadow-lg shadow-green-500/20"
				>
					CONFIRMAR RESPOSTA
				</button>
			)}

			{/* Feedback */}
			{confirmada && (
				<div
					className={`text-center py-5 rounded-xl font-black text-xl border-2 ${
						selecionada === questao.resposta
							? "bg-green-500/20 text-green-300 border-green-400/50"
							: "bg-red-500/20 text-red-300 border-red-400/50"
					}`}
				>
					{selecionada === questao.resposta
						? "RESPOSTA CERTA!"
						: `ERROU! A resposta era a alternativa ${questao.resposta}.`}
				</div>
			)}
		</div>
	);
}
