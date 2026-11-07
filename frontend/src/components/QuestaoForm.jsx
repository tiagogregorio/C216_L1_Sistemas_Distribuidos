import { useState } from "react";
import { validarQuestao } from "../validation";

const CAMPOS_VAZIOS = {
	ano: 2019,
	numero: 1,
	tipo: "CE",
	enunciado: "",
	alternativa_a: "",
	alternativa_b: "",
	alternativa_c: "",
	alternativa_d: "",
	alternativa_e: "",
	resposta: "A",
	assunto: "",
	dificuldade: "medio",
};

export default function QuestaoForm({ onSubmit, inicial = null }) {
	const [dados, setDados] = useState(inicial || CAMPOS_VAZIOS);
	const [erros, setErros] = useState({});
	const [enviando, setEnviando] = useState(false);

	function handleChange(campo, valor) {
		setDados((prev) => ({ ...prev, [campo]: valor }));
		setErros((prev) => ({ ...prev, [campo]: undefined }));
	}

	async function handleSubmit(e) {
		e.preventDefault();
		const validacao = validarQuestao(dados);
		if (Object.keys(validacao).length > 0) {
			setErros(validacao);
			return;
		}
		setEnviando(true);
		try {
			await onSubmit({ ...dados, ano: Number(dados.ano), numero: Number(dados.numero) });
			if (!inicial) setDados(CAMPOS_VAZIOS);
			setErros({});
		} catch (err) {
			setErros({ geral: err.message });
		} finally {
			setEnviando(false);
		}
	}

	const inputClass =
		"w-full bg-[var(--cor-fundo)] border border-[var(--cor-borda)] rounded-lg px-3 py-2 text-[var(--cor-texto)] focus:border-[var(--cor-destaque)] focus:outline-none";

	return (
		<form onSubmit={handleSubmit} className="space-y-4">
			{erros.geral && (
				<div role="alert" className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-2 rounded-lg">
					{erros.geral}
				</div>
			)}

			<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div>
					<label className="block text-sm mb-1">Ano</label>
					<input type="number" value={dados.ano} onChange={(e) => handleChange("ano", e.target.value)} className={inputClass} />
					{erros.ano && <p className="text-red-400 text-xs mt-1">{erros.ano}</p>}
				</div>
				<div>
					<label className="block text-sm mb-1">Numero</label>
					<input type="number" value={dados.numero} onChange={(e) => handleChange("numero", e.target.value)} className={inputClass} />
					{erros.numero && <p className="text-red-400 text-xs mt-1">{erros.numero}</p>}
				</div>
				<div>
					<label className="block text-sm mb-1">Tipo</label>
					<select value={dados.tipo} onChange={(e) => handleChange("tipo", e.target.value)} className={inputClass}>
						<option value="CE">Componente Especifico</option>
						<option value="FG">Formacao Geral</option>
					</select>
				</div>
				<div>
					<label className="block text-sm mb-1">Dificuldade</label>
					<select value={dados.dificuldade || ""} onChange={(e) => handleChange("dificuldade", e.target.value || null)} className={inputClass}>
						<option value="">Nao definida</option>
						<option value="facil">Facil</option>
						<option value="medio">Medio</option>
						<option value="dificil">Dificil</option>
					</select>
				</div>
			</div>

			<div>
				<label className="block text-sm mb-1">Assunto</label>
				<input type="text" value={dados.assunto || ""} onChange={(e) => handleChange("assunto", e.target.value)} className={inputClass} placeholder="Ex: Algoritmos de Ordenacao" />
			</div>

			<div>
				<label className="block text-sm mb-1">Enunciado</label>
				<textarea rows={4} value={dados.enunciado} onChange={(e) => handleChange("enunciado", e.target.value)} className={inputClass} placeholder="Texto completo da questao..." />
				{erros.enunciado && <p className="text-red-400 text-xs mt-1">{erros.enunciado}</p>}
			</div>

			{["a", "b", "c", "d", "e"].map((letra) => (
				<div key={letra}>
					<label className="block text-sm mb-1">Alternativa {letra.toUpperCase()}</label>
					<input
						type="text"
						value={dados[`alternativa_${letra}`]}
						onChange={(e) => handleChange(`alternativa_${letra}`, e.target.value)}
						className={inputClass}
					/>
					{erros[`alternativa_${letra}`] && <p className="text-red-400 text-xs mt-1">{erros[`alternativa_${letra}`]}</p>}
				</div>
			))}

			<div>
				<label className="block text-sm mb-1">Resposta correta</label>
				<select value={dados.resposta} onChange={(e) => handleChange("resposta", e.target.value)} className={inputClass}>
					{["A", "B", "C", "D", "E"].map((l) => (
						<option key={l} value={l}>{l}</option>
					))}
				</select>
			</div>

			<button type="submit" disabled={enviando} className="w-full bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold py-3 rounded-lg hover:brightness-110 transition disabled:opacity-50 cursor-pointer">
				{enviando ? "Salvando..." : inicial ? "Atualizar Questao" : "Cadastrar Questao"}
			</button>
		</form>
	);
}
