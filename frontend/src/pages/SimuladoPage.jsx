import { useEffect, useState } from "react";
import QuizQuestao from "../components/QuizQuestao";
import { buscarQuestao, submeterRespostas } from "../services/api";
import { useSound } from "../sound/SoundContext";
import {
	lerProgresso,
	limparProgresso,
	salvarProgresso,
} from "../utils/progressoSimulado";

export default function SimuladoPage({
	simuladoId,
	questaoIds,
	onVoltar,
	onParar,
}) {
	const progressoSalvo = lerProgresso(simuladoId);
	const [questoes, setQuestoes] = useState([]);
	const [indiceAtual, setIndiceAtual] = useState(
		progressoSalvo?.indiceAtual ?? 0,
	);
	const [respostas, setRespostas] = useState(progressoSalvo?.respostas ?? []);
	const [resultado, setResultado] = useState(null);
	const [loading, setLoading] = useState(true);
	const [erro, setErro] = useState(null);
	const { setMusicaAtiva } = useSound();

	// Musica de fundo toca enquanto o usuario esta no simulado (ajuda na
	// concentracao) e para automaticamente ao sair desta pagina.
	useEffect(() => {
		setMusicaAtiva(true);
		return () => setMusicaAtiva(false);
	}, [setMusicaAtiva]);

	useEffect(() => {
		async function carregarQuestoes() {
			try {
				const promises = questaoIds.map((id) => buscarQuestao(id));
				const todas = await Promise.all(promises);
				setQuestoes(todas);
			} catch (err) {
				setErro(err.message);
			} finally {
				setLoading(false);
			}
		}
		carregarQuestoes();
	}, [questaoIds]);

	// Salva o progresso (questao atual + respostas) a cada mudanca, para que
	// atualizar a pagina (F5) continue de onde o usuario parou.
	useEffect(() => {
		if (resultado) return;
		salvarProgresso(simuladoId, { indiceAtual, respostas });
	}, [simuladoId, indiceAtual, respostas, resultado]);

	async function handleResponder(resposta) {
		const novasRespostas = [...respostas, resposta];
		setRespostas(novasRespostas);

		if (indiceAtual < questoes.length - 1) {
			setIndiceAtual(indiceAtual + 1);
		} else {
			try {
				const payload = novasRespostas.map((r) => ({
					questao_id: r.questao_id,
					alternativa_escolhida: r.alternativa_escolhida,
					tempo_resposta: r.tempo_resposta,
				}));
				const res = await submeterRespostas(simuladoId, payload);
				setResultado(res);
				limparProgresso(simuladoId);
			} catch (err) {
				setErro(err.message);
			}
		}
	}

	function handleParar() {
		// Nao limpa o progresso: o simulado fica salvo para ser retomado
		// depois pelo botao "Continuar" no Historico.
		onParar();
	}

	if (loading) {
		return (
			<div className="flex items-center justify-center py-24">
				<p className="text-gray-400 text-lg">
					Carregando questoes do simulado...
				</p>
			</div>
		);
	}

	if (erro) {
		return (
			<div className="max-w-2xl mx-auto p-6">
				<div
					role="alert"
					className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4"
				>
					{erro}
				</div>
				<button
					type="button"
					onClick={onVoltar}
					className="text-[var(--cor-destaque)] cursor-pointer"
				>
					Voltar
				</button>
			</div>
		);
	}

	if (resultado) {
		const tempoTotal = respostas.reduce(
			(acc, r) => acc + (r.tempo_resposta || 0),
			0,
		);
		const tempoMedio = respostas.length > 0 ? tempoTotal / respostas.length : 0;

		return (
			<div className="max-w-2xl mx-auto p-6">
				<div className="text-center mb-8">
					<h1 className="text-3xl font-bold text-[var(--cor-destaque)] mb-2">
						Resultado
					</h1>
					<p className="text-gray-400">{resultado.nome}</p>
				</div>

				<div className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-2xl p-8 text-center mb-8">
					<div
						className="text-6xl font-bold mb-4"
						style={{
							color:
								resultado.nota >= 60 ? "var(--cor-acerto)" : "var(--cor-erro)",
						}}
					>
						{resultado.nota?.toFixed(1)}%
					</div>
					<p className="text-xl text-gray-300 mb-6">
						{resultado.acertos} de {resultado.total_questoes} questoes corretas
					</p>

					<div className="grid grid-cols-3 gap-4 text-center">
						<div className="bg-[var(--cor-fundo)] rounded-xl p-4">
							<div className="text-2xl font-bold text-[var(--cor-destaque)]">
								{resultado.acertos}
							</div>
							<div className="text-sm text-gray-400">Acertos</div>
						</div>
						<div className="bg-[var(--cor-fundo)] rounded-xl p-4">
							<div className="text-2xl font-bold text-[var(--cor-destaque)]">
								{Math.floor(tempoTotal / 60)}:
								{(tempoTotal % 60).toString().padStart(2, "0")}
							</div>
							<div className="text-sm text-gray-400">Tempo total</div>
						</div>
						<div className="bg-[var(--cor-fundo)] rounded-xl p-4">
							<div className="text-2xl font-bold text-[var(--cor-destaque)]">
								{tempoMedio.toFixed(0)}s
							</div>
							<div className="text-sm text-gray-400">Media/questao</div>
						</div>
					</div>
				</div>

				<div className="space-y-2 mb-8">
					{respostas.map((r, i) => (
						<div
							key={r.questao_id}
							className={`flex items-center justify-between p-3 rounded-lg ${
								r.correta
									? "bg-[var(--cor-acerto)]/10"
									: "bg-[var(--cor-erro)]/10"
							}`}
						>
							<span className="text-sm">Questao {i + 1}</span>
							<div className="flex items-center gap-3">
								<span className="text-xs text-gray-400">
									{r.tempo_resposta}s
								</span>
								<span
									className={`font-bold ${r.correta ? "text-[var(--cor-acerto)]" : "text-[var(--cor-erro)]"}`}
								>
									{r.correta ? "Correta" : `Errou (${r.alternativa_escolhida})`}
								</span>
							</div>
						</div>
					))}
				</div>

				<button
					type="button"
					onClick={onVoltar}
					className="w-full bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold py-4 rounded-xl text-lg hover:brightness-110 transition cursor-pointer"
				>
					Voltar ao Menu
				</button>
			</div>
		);
	}

	return (
		<div className="p-6">
			<div className="flex items-center gap-4 mb-4">
				<div className="flex-1 bg-[var(--cor-borda)] rounded-full h-2">
					<div
						className="bg-[var(--cor-destaque)] h-2 rounded-full transition-all duration-500"
						style={{ width: `${((indiceAtual + 1) / questoes.length) * 100}%` }}
					/>
				</div>
				<button
					type="button"
					onClick={handleParar}
					title="Encerra o simulado e volta para o dashboard"
					className="shrink-0 px-4 py-1.5 rounded-lg border-2 border-red-500/50 text-red-300 text-xs font-bold uppercase tracking-wider hover:bg-red-900/30 transition-colors cursor-pointer"
				>
					Parar
				</button>
			</div>
			<QuizQuestao
				questao={questoes[indiceAtual]}
				numero={indiceAtual + 1}
				total={questoes.length}
				onResponder={handleResponder}
			/>
		</div>
	);
}
