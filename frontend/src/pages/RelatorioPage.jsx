import { useEffect, useState } from "react";
import { relatorioSimulados } from "../services/api";

export default function RelatorioPage() {
	const [dados, setDados] = useState(null);
	const [loading, setLoading] = useState(true);
	const [erro, setErro] = useState(null);

	useEffect(() => {
		relatorioSimulados()
			.then(setDados)
			.catch((err) => setErro(err.message))
			.finally(() => setLoading(false));
	}, []);

	if (loading) {
		return (
			<div className="flex items-center justify-center py-24">
				<p className="text-gray-400 text-lg">Carregando relatorio...</p>
			</div>
		);
	}

	if (erro) {
		return (
			<div className="max-w-3xl mx-auto p-6">
				<div
					role="alert"
					className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg"
				>
					{erro}
				</div>
			</div>
		);
	}

	if (!dados || dados.total_questoes_respondidas === 0) {
		return (
			<div className="max-w-3xl mx-auto p-6 text-center py-16">
				<h1 className="text-2xl font-bold text-[var(--cor-destaque)] mb-3">
					Relatorio
				</h1>
				<p className="text-gray-400">
					Responda ao menos um simulado para gerar seu relatorio de desempenho.
				</p>
			</div>
		);
	}

	return (
		<div className="max-w-3xl mx-auto p-6">
			<div className="text-center mb-8">
				<h1 className="text-3xl font-bold text-[var(--cor-destaque)] mb-2">
					Relatorio de Estudo
				</h1>
				<p className="text-gray-400">
					{dados.total_questoes_respondidas} questoes respondidas ·{" "}
					{dados.taxa_acerto_geral}% de acerto geral
				</p>
			</div>

			{dados.prioridades_de_estudo?.length > 0 ? (
				<div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-6 mb-6">
					<h2 className="text-lg font-bold text-amber-300 mb-3">
						Prioridades de estudo
					</h2>
					<p className="text-amber-100/80 text-sm mb-4">
						Esses assuntos sao onde voce mais precisa focar antes da prova,
						ordenados do mais fraco para o mais forte.
					</p>
					<ol className="space-y-2">
						{dados.prioridades_de_estudo.map((item, i) => (
							<li
								key={item.assunto}
								className="flex items-center justify-between bg-black/20 rounded-lg px-4 py-2"
							>
								<span className="text-sm">
									<span className="text-amber-400 font-bold mr-2">
										{i + 1}.
									</span>
									{item.assunto}
								</span>
								<span className="text-sm font-mono text-amber-300">
									{item.taxa}% ({item.acertos}/{item.total})
								</span>
							</li>
						))}
					</ol>
				</div>
			) : (
				<div className="bg-[var(--cor-acerto)]/10 border border-[var(--cor-acerto)]/30 rounded-xl p-6 mb-6 text-center">
					<p className="text-[var(--cor-acerto)] font-bold">
						Nenhum assunto com desempenho abaixo de 70%. Continue assim!
					</p>
				</div>
			)}

			<div className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-6">
				<h2 className="text-lg font-bold mb-1">Questoes para revisar</h2>
				<p className="text-gray-400 text-sm mb-4">
					As questoes que voce errou, mais recentes primeiro.
				</p>

				{dados.questoes_erradas?.length === 0 ? (
					<p className="text-[var(--cor-acerto)] text-sm">
						Voce nao errou nenhuma questao ate agora. Excelente!
					</p>
				) : (
					<div className="space-y-3">
						{dados.questoes_erradas.map((q) => (
							<div
								key={`${q.questao_id}-${q.alternativa_escolhida}`}
								className="bg-[var(--cor-fundo)] border border-[var(--cor-borda)] rounded-lg p-4"
							>
								<div className="flex items-center gap-2 mb-2 text-xs text-gray-400">
									<span className="bg-black/30 px-2 py-0.5 rounded">
										ENADE {q.ano}
									</span>
									<span>Questao {q.numero}</span>
									{q.assunto && <span>· {q.assunto}</span>}
								</div>
								<p className="text-sm text-gray-200 mb-2 line-clamp-2">
									{q.enunciado}
								</p>
								<div className="flex items-center gap-4 text-sm">
									<span className="text-[var(--cor-erro)]">
										Sua resposta: {q.alternativa_escolhida ?? "-"}
									</span>
									<span className="text-[var(--cor-acerto)]">
										Correta: {q.resposta_correta}
									</span>
								</div>
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	);
}
