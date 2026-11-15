import { useEffect, useRef, useState } from "react";
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
	// Respostas guardadas por questao_id, para permitir navegar livremente
	// (Voltar/Avancar) e revisar questoes ja respondidas sem perder o resto.
	const [respostasPorQuestao, setRespostasPorQuestao] = useState(
		progressoSalvo?.respostasPorQuestao ?? {},
	);
	const [resultado, setResultado] = useState(null);
	const [loading, setLoading] = useState(true);
	const [erro, setErro] = useState(null);
	const { setMusicaAtiva } = useSound();
	const timeoutAvancoRef = useRef(null);

	// Musica de fundo toca enquanto o usuario esta no simulado (ajuda na
	// concentracao) e para automaticamente ao sair desta pagina.
	useEffect(() => {
		setMusicaAtiva(true);
		return () => setMusicaAtiva(false);
	}, [setMusicaAtiva]);

	// Cancela o avanco automatico pendente se a pagina for desmontada antes
	// dele disparar (ex.: usuario clicou Finalizar ou Parar logo em seguida).
	useEffect(() => {
		return () => clearTimeout(timeoutAvancoRef.current);
	}, []);

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
		salvarProgresso(simuladoId, { indiceAtual, respostasPorQuestao });
	}, [simuladoId, indiceAtual, respostasPorQuestao, resultado]);

	function handleResponder(resposta) {
		setRespostasPorQuestao((anterior) => ({
			...anterior,
			[resposta.questao_id]: resposta,
		}));

		// Avanca automaticamente apos confirmar, dando um instante para ver o
		// feedback (certo/errado). Se o usuario ja tiver navegado manualmente
		// nesse meio-tempo, respeita a posicao atual em vez de pular por cima.
		const indiceRespondido = indiceAtual;
		timeoutAvancoRef.current = setTimeout(() => {
			setIndiceAtual((atual) => {
				if (atual !== indiceRespondido) return atual;
				return Math.min(questoes.length - 1, atual + 1);
			});
		}, 1200);
	}

	function handleVoltar() {
		setIndiceAtual((i) => Math.max(0, i - 1));
	}

	function handleAvancar() {
		setIndiceAtual((i) => Math.min(questoes.length - 1, i + 1));
	}

	async function handleFinalizar() {
		const respostas = Object.values(respostasPorQuestao);
		if (respostas.length === 0) return;
		if (
			respostas.length < questoes.length &&
			!confirm(
				`Voce respondeu ${respostas.length} de ${questoes.length} questoes. ` +
					"As nao respondidas contarao como erradas. Finalizar mesmo assim?",
			)
		) {
			return;
		}
		try {
			const payload = respostas.map((r) => ({
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
		// Ordem das questoes do simulado, nao a ordem em que foram respondidas.
		const respostasOrdenadas = questoes
			.map((q) => respostasPorQuestao[q.id])
			.filter(Boolean);
		const tempoTotal = respostasOrdenadas.reduce(
			(acc, r) => acc + (r.tempo_resposta || 0),
			0,
		);
		const tempoMedio =
			respostasOrdenadas.length > 0
				? tempoTotal / respostasOrdenadas.length
				: 0;
		const respondidas = resultado.respondidas ?? respostasOrdenadas.length;
		const incompleto = respondidas < resultado.total_questoes;
		const taxaNasRespondidas =
			respondidas > 0 ? (resultado.acertos / respondidas) * 100 : 0;

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
						className="text-6xl font-bold mb-2"
						style={{
							color:
								resultado.nota >= 60 ? "var(--cor-acerto)" : "var(--cor-erro)",
						}}
					>
						{resultado.nota?.toFixed(1)}%
					</div>
					<p className="text-xs text-gray-500 mb-4">
						Nota estilo ENADE — questoes nao respondidas contam como erro
					</p>
					<p className="text-xl text-gray-300 mb-2">
						{resultado.acertos} de {resultado.total_questoes} questoes corretas
					</p>

					{incompleto && (
						<div className="bg-amber-900/20 border border-amber-500/30 rounded-lg px-4 py-3 mt-4 mb-2 text-left">
							<p className="text-amber-300 text-sm font-bold mb-1">
								Simulado finalizado antes do fim ({respondidas} de{" "}
								{resultado.total_questoes} respondidas)
							</p>
							<p className="text-amber-100/80 text-sm">
								Nas questoes que voce de fato respondeu, seu acerto foi{" "}
								<strong>{taxaNasRespondidas.toFixed(1)}%</strong>. A nota acima
								segue o criterio real do ENADE, em que deixar em branco conta
								como erro — por isso pode parecer mais baixa do que o quanto
								voce realmente acertou.
							</p>
						</div>
					)}

					<div className="grid grid-cols-3 gap-4 text-center mt-6">
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
					{respostasOrdenadas.map((r, i) => (
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

	const respondidas = questoes.map((q) => Boolean(respostasPorQuestao[q.id]));
	const totalRespondidas = respondidas.filter(Boolean).length;

	return (
		<div className="p-6">
			<div className="flex items-center gap-2 mb-4 flex-wrap">
				<div className="flex-1 min-w-[120px] bg-[var(--cor-borda)] rounded-full h-2">
					<div
						className="bg-[var(--cor-destaque)] h-2 rounded-full transition-all duration-500"
						style={{ width: `${(totalRespondidas / questoes.length) * 100}%` }}
					/>
				</div>
				<button
					type="button"
					onClick={handleVoltar}
					disabled={indiceAtual === 0}
					title="Questao anterior"
					className="shrink-0 px-3 py-1.5 rounded-lg border-2 border-[var(--cor-borda)] text-gray-300 text-xs font-bold hover:border-gray-500 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
				>
					◀ Voltar
				</button>
				<button
					type="button"
					onClick={handleAvancar}
					disabled={indiceAtual === questoes.length - 1}
					title="Proxima questao"
					className="shrink-0 px-3 py-1.5 rounded-lg border-2 border-[var(--cor-borda)] text-gray-300 text-xs font-bold hover:border-gray-500 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
				>
					Avancar ▶
				</button>
				<button
					type="button"
					onClick={handleFinalizar}
					disabled={totalRespondidas === 0}
					title="Envia as respostas e mostra o resultado"
					className="shrink-0 px-4 py-1.5 rounded-lg border-2 border-[var(--cor-acerto)]/60 text-[var(--cor-acerto)] text-xs font-bold uppercase tracking-wider hover:bg-[var(--cor-acerto)]/10 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
				>
					Finalizar
				</button>
				<button
					type="button"
					onClick={handleParar}
					title="Encerra por agora e volta para o dashboard (pode continuar depois)"
					className="shrink-0 px-4 py-1.5 rounded-lg border-2 border-red-500/50 text-red-300 text-xs font-bold uppercase tracking-wider hover:bg-red-900/30 transition-colors cursor-pointer"
				>
					Parar
				</button>
			</div>
			<QuizQuestao
				questao={questoes[indiceAtual]}
				numero={indiceAtual + 1}
				total={questoes.length}
				respostaSalva={respostasPorQuestao[questoes[indiceAtual].id] ?? null}
				respondidas={respondidas}
				onResponder={handleResponder}
			/>
		</div>
	);
}
