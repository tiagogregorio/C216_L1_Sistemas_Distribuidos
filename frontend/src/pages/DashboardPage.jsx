import { useState, useEffect } from "react";
import { dashboard as fetchDashboard, resumoQuestoes } from "../services/api";

export default function DashboardPage() {
	const [dados, setDados] = useState(null);
	const [resumo, setResumo] = useState(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		async function carregar() {
			try {
				const [d, r] = await Promise.all([fetchDashboard(), resumoQuestoes()]);
				setDados(d);
				setResumo(r);
			} catch {
				// Dashboard vazio e aceitavel
			} finally {
				setLoading(false);
			}
		}
		carregar();
	}, []);

	if (loading) {
		return <p className="text-gray-400 text-center py-12">Carregando dashboard...</p>;
	}

	const cards = [
		{ label: "Questoes no Banco", valor: resumo?.total || 0, cor: "text-[var(--cor-destaque)]" },
		{ label: "Simulados Realizados", valor: dados?.simulados_finalizados || 0, cor: "text-[var(--cor-destaque)]" },
		{ label: "Taxa de Acerto Geral", valor: `${dados?.taxa_acerto_geral || 0}%`, cor: dados?.taxa_acerto_geral >= 60 ? "text-[var(--cor-acerto)]" : "text-[var(--cor-erro)]" },
		{ label: "Media dos Simulados", valor: dados?.media_nota != null ? `${dados.media_nota}%` : "-", cor: "text-[var(--cor-destaque)]" },
	];

	return (
		<div className="max-w-6xl mx-auto p-6">
			<h1 className="text-2xl font-bold text-[var(--cor-destaque)] mb-6">Dashboard de Desempenho</h1>

			<div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
				{cards.map((c) => (
					<div key={c.label} className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-6 text-center">
						<div className={`text-3xl font-bold mb-2 ${c.cor}`}>{c.valor}</div>
						<div className="text-sm text-gray-400">{c.label}</div>
					</div>
				))}
			</div>

			{dados?.desempenho_por_ano?.length > 0 && (
				<div className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-6 mb-6">
					<h2 className="text-lg font-bold mb-4">Desempenho por Ano</h2>
					<div className="space-y-3">
						{dados.desempenho_por_ano.map((item) => (
							<div key={item.ano} className="flex items-center gap-4">
								<span className="text-[var(--cor-destaque)] font-mono font-bold w-16">{item.ano}</span>
								<div className="flex-1 bg-[var(--cor-fundo)] rounded-full h-6 overflow-hidden">
									<div
										className="h-full rounded-full transition-all"
										style={{
											width: `${item.taxa}%`,
											backgroundColor: item.taxa >= 60 ? "var(--cor-acerto)" : item.taxa >= 40 ? "var(--cor-destaque)" : "var(--cor-erro)",
										}}
									/>
								</div>
								<span className="text-sm font-mono w-20 text-right">
									{item.acertos}/{item.total} ({item.taxa}%)
								</span>
							</div>
						))}
					</div>
				</div>
			)}

			{dados?.desempenho_por_tipo?.length > 0 && (
				<div className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-6">
					<h2 className="text-lg font-bold mb-4">Desempenho por Tipo</h2>
					<div className="grid grid-cols-2 gap-4">
						{dados.desempenho_por_tipo.map((item) => (
							<div key={item.tipo} className="bg-[var(--cor-fundo)] rounded-xl p-6 text-center">
								<div className="text-sm text-gray-400 mb-2">
									{item.tipo === "CE" ? "Componente Especifico" : "Formacao Geral"}
								</div>
								<div className="text-3xl font-bold" style={{
									color: item.taxa >= 60 ? "var(--cor-acerto)" : "var(--cor-erro)",
								}}>
									{item.taxa}%
								</div>
								<div className="text-xs text-gray-500 mt-1">
									{item.acertos}/{item.total} acertos
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{(!dados || dados.simulados_finalizados === 0) && (
				<div className="text-center py-12 text-gray-500">
					Realize seu primeiro simulado para ver as estatisticas aqui.
				</div>
			)}
		</div>
	);
}
