import { useEffect, useState } from "react";
import { listarSimulados, removerSimulado } from "../services/api";

export default function HistoricoPage() {
	const [simulados, setSimulados] = useState([]);
	const [loading, setLoading] = useState(true);
	const [erro, setErro] = useState(null);

	async function carregar() {
		setLoading(true);
		try {
			const dados = await listarSimulados();
			setSimulados(dados);
		} catch (err) {
			setErro(err.message);
		} finally {
			setLoading(false);
		}
	}

	useEffect(() => {
		carregar();
	}, []);

	async function handleRemover(id) {
		if (!confirm("Remover este simulado?")) return;
		try {
			await removerSimulado(id);
			carregar();
		} catch (err) {
			setErro(err.message);
		}
	}

	if (loading)
		return <p className="text-gray-400 text-center py-12">Carregando...</p>;

	return (
		<div className="max-w-4xl mx-auto p-6">
			<h1 className="text-2xl font-bold text-[var(--cor-destaque)] mb-6">
				Historico de Simulados
			</h1>

			{erro && (
				<div
					role="alert"
					className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4"
				>
					{erro}
				</div>
			)}

			{simulados.length === 0 ? (
				<p className="text-gray-500 text-center py-12">
					Nenhum simulado realizado ainda.
				</p>
			) : (
				<div className="space-y-3">
					{simulados.map((s) => (
						<div
							key={s.id}
							className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-5 flex items-center justify-between"
						>
							<div>
								<h3 className="font-bold text-lg">{s.nome}</h3>
								<p className="text-sm text-gray-400">
									{new Date(s.criado_em).toLocaleDateString("pt-BR")} —{" "}
									{s.total_questoes} questoes
								</p>
							</div>
							<div className="flex items-center gap-6">
								{s.finalizado ? (
									<div className="text-right">
										<div
											className="text-2xl font-bold"
											style={{
												color:
													(s.nota || 0) >= 60
														? "var(--cor-acerto)"
														: "var(--cor-erro)",
											}}
										>
											{s.nota?.toFixed(1)}%
										</div>
										<div className="text-xs text-gray-400">
											{s.acertos}/{s.total_questoes} acertos
										</div>
									</div>
								) : (
									<span className="text-yellow-400 text-sm">Em andamento</span>
								)}
								<button
									type="button"
									onClick={() => handleRemover(s.id)}
									className="text-red-400 hover:text-red-300 text-sm cursor-pointer"
								>
									Remover
								</button>
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
