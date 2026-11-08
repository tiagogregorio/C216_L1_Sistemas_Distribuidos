import { useCallback, useEffect, useState } from "react";
import QuestaoForm from "../components/QuestaoForm";
import { criarQuestao, listarQuestoes, removerQuestao } from "../services/api";

export default function QuestoesPage() {
	const [questoes, setQuestoes] = useState([]);
	const [loading, setLoading] = useState(true);
	const [erro, setErro] = useState(null);
	const [mostrarForm, setMostrarForm] = useState(false);
	const [filtroAno, setFiltroAno] = useState("");
	const [filtroTipo, setFiltroTipo] = useState("");

	const carregar = useCallback(async () => {
		setLoading(true);
		setErro(null);
		try {
			const filtros = {};
			if (filtroAno) filtros.ano = filtroAno;
			if (filtroTipo) filtros.tipo = filtroTipo;
			const dados = await listarQuestoes(filtros);
			setQuestoes(dados);
		} catch (err) {
			setErro(err.message);
		} finally {
			setLoading(false);
		}
	}, [filtroAno, filtroTipo]);

	useEffect(() => {
		carregar();
	}, [carregar]);

	async function handleCriar(dados) {
		await criarQuestao(dados);
		setMostrarForm(false);
		carregar();
	}

	async function handleRemover(id) {
		if (!confirm("Remover esta questao?")) return;
		try {
			await removerQuestao(id);
			carregar();
		} catch (err) {
			setErro(err.message);
		}
	}

	const selectClass =
		"bg-[var(--cor-fundo)] border border-[var(--cor-borda)] rounded-lg px-3 py-2 text-[var(--cor-texto)] text-sm";

	return (
		<div className="max-w-6xl mx-auto p-6">
			<div className="flex items-center justify-between mb-6">
				<h1 className="text-2xl font-bold text-[var(--cor-destaque)]">
					Banco de Questoes
				</h1>
				<button
					type="button"
					onClick={() => setMostrarForm(!mostrarForm)}
					className="bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold px-6 py-2 rounded-lg hover:brightness-110 transition cursor-pointer"
				>
					{mostrarForm ? "Fechar" : "+ Nova Questao"}
				</button>
			</div>

			{mostrarForm && (
				<div className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-6 mb-6">
					<h2 className="text-lg font-bold mb-4">Cadastrar Questao</h2>
					<QuestaoForm onSubmit={handleCriar} />
				</div>
			)}

			<div className="flex gap-4 mb-6">
				<select
					value={filtroAno}
					onChange={(e) => setFiltroAno(e.target.value)}
					className={selectClass}
				>
					<option value="">Todos os anos</option>
					<option value="2014">2014</option>
					<option value="2017">2017</option>
					<option value="2019">2019</option>
					<option value="2023">2023</option>
				</select>
				<select
					value={filtroTipo}
					onChange={(e) => setFiltroTipo(e.target.value)}
					className={selectClass}
				>
					<option value="">Todos os tipos</option>
					<option value="CE">Componente Especifico</option>
					<option value="FG">Formacao Geral</option>
				</select>
			</div>

			{erro && (
				<div
					role="alert"
					className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-4"
				>
					{erro}
				</div>
			)}

			{loading ? (
				<p className="text-gray-400 text-center py-12">
					Carregando questoes...
				</p>
			) : questoes.length === 0 ? (
				<p className="text-gray-400 text-center py-12">
					Nenhuma questao encontrada.
				</p>
			) : (
				<div className="space-y-3">
					{questoes.map((q) => (
						<div
							key={q.id}
							className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-4 flex items-center justify-between"
						>
							<div className="flex items-center gap-4">
								<span className="bg-[var(--cor-destaque)]/20 text-[var(--cor-destaque)] font-mono font-bold px-3 py-1 rounded-lg text-sm">
									{q.ano}
								</span>
								<span className="text-sm text-gray-400">Q{q.numero}</span>
								<span
									className={`text-xs px-2 py-0.5 rounded font-medium ${
										q.tipo === "CE"
											? "bg-blue-900/40 text-blue-300"
											: "bg-purple-900/40 text-purple-300"
									}`}
								>
									{q.tipo === "CE" ? "Comp. Especifico" : "Form. Geral"}
								</span>
								{q.dificuldade && (
									<span
										className={`text-xs px-2 py-0.5 rounded ${
											q.dificuldade === "facil"
												? "bg-green-900/40 text-green-300"
												: q.dificuldade === "medio"
													? "bg-yellow-900/40 text-yellow-300"
													: "bg-red-900/40 text-red-300"
										}`}
									>
										{q.dificuldade}
									</span>
								)}
								{q.assunto && (
									<span className="text-xs text-gray-500">{q.assunto}</span>
								)}
							</div>
							<button
								type="button"
								onClick={() => handleRemover(q.id)}
								className="text-red-400 hover:text-red-300 text-sm cursor-pointer"
							>
								Remover
							</button>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
