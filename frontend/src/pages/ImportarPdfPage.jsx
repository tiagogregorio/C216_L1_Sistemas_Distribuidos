import { useEffect, useState } from "react";
import {
	atualizarQuestao,
	classificarQuestoesLote,
	criarQuestao,
	importarPdf,
	listarQuestoes,
	statusIA,
} from "../services/api";
import { redimensionarImagem } from "../utils/redimensionarImagem";

const CAMPO_CLASS =
	"w-full bg-[var(--cor-fundo)] border border-[var(--cor-borda)] rounded-lg px-3 py-2 text-sm";
const TAMANHO_LOTE_IA = 10;
const FALHAS_DE_REDE_PARA_INTERROMPER = 3;
const LETRAS = ["a", "b", "c", "d", "e"];

const ROTULO_RESULTADO = {
	criada: "✓ Salva",
	atualizada: "✓ Pagina anexada a questao existente",
	ignorada: "Ja existia — nada a anexar",
};

// Campos que existem so na tela de revisao e nao fazem parte da questao.
function dadosDaQuestao(rascunho) {
	const {
		pagina,
		alternativas_incompletas,
		sem_texto,
		mistura_possivel,
		salva,
		descartada,
		resultado,
		existenteId,
		existenteRotulo,
		erroLote,
		...dados
	} = rascunho;
	return dados;
}

function textoCompleto(r) {
	return (
		r.enunciado.trim().length >= 10 &&
		LETRAS.every((l) => r[`alternativa_${l}`].trim())
	);
}

// Em paginas de duas colunas o texto pode faltar (sem_texto) ou ter vindo
// misturado com a questao vizinha (mistura_possivel): exige olho humano.
function precisaRevisao(r) {
	return Boolean(r.sem_texto || r.mistura_possivel);
}

// Pode ser gravada agora? Existente so precisa da pagina; nova precisa de texto.
function salvavel(r, paginaImagem, anexarSeExistir) {
	if (r.existenteId && anexarSeExistir) return Boolean(paginaImagem);
	return textoCompleto(r);
}

// "Salvar todas" so grava o que nao precisa de revisao humana.
function elegivelParaLote(r, paginaImagem, anexarSeExistir) {
	if (r.existenteId && anexarSeExistir) return Boolean(paginaImagem);
	return textoCompleto(r) && !precisaRevisao(r);
}

function camposParaIA(r) {
	return {
		enunciado: r.enunciado,
		alternativa_a: r.alternativa_a,
		alternativa_b: r.alternativa_b,
		alternativa_c: r.alternativa_c,
		alternativa_d: r.alternativa_d,
		alternativa_e: r.alternativa_e,
	};
}

/**
 * Grava um rascunho. Se a questao ja existe (mesmo ano e numero) e a opcao
 * "anexar se existir" esta ligada, nao cria duplicata: so anexa a pagina.
 * Devolve "criada", "atualizada" ou "ignorada".
 */
async function persistirRascunho(rascunho, paginaImagem, anexarSeExistir) {
	if (rascunho.existenteId && anexarSeExistir) {
		if (!paginaImagem) return "ignorada";
		await atualizarQuestao(rascunho.existenteId, {
			pagina_original: paginaImagem,
		});
		return "atualizada";
	}
	const dados = dadosDaQuestao(rascunho);
	if (paginaImagem) dados.pagina_original = paginaImagem;
	await criarQuestao(dados);
	return "criada";
}

function textoResumo({ contagem, erros, puladas, abortado }) {
	const partes = [
		`${contagem.criada} nova(s) salva(s)`,
		`${contagem.atualizada} existente(s) com pagina anexada`,
		`${contagem.ignorada} ja existente(s) ignorada(s)`,
	];
	if (puladas > 0) {
		partes.push(`${puladas} pulada(s) por precisarem de revisao manual`);
	}
	if (erros.length > 0) partes.push(`${erros.length} com erro`);
	let texto = `${partes.join(", ")}.`;
	if (abortado) {
		texto += " Envio interrompido: o servidor parou de responder.";
	}
	return texto;
}

function RascunhoCard({
	rascunho,
	atualizar,
	onPaginaClick,
	anexarSeExistir,
	paginaImagem,
}) {
	const [enviando, setEnviando] = useState(false);
	const [erro, setErro] = useState(null);

	async function handleImagem(e) {
		const arquivo = e.target.files?.[0];
		if (!arquivo) return;
		try {
			const dataUri = await redimensionarImagem(arquivo);
			atualizar({ imagem: dataUri });
		} catch (err) {
			setErro(err.message);
		}
	}

	async function salvar() {
		setEnviando(true);
		setErro(null);
		try {
			const resultado = await persistirRascunho(
				rascunho,
				paginaImagem,
				anexarSeExistir,
			);
			atualizar({ salva: true, resultado, erroLote: null });
		} catch (err) {
			setErro(err.message);
		} finally {
			setEnviando(false);
		}
	}

	if (rascunho.descartada) return null;

	const apenasAnexar = Boolean(rascunho.existenteId) && anexarSeExistir;
	const salvavelAgora = salvavel(rascunho, paginaImagem, anexarSeExistir);
	const mensagemErro = erro || rascunho.erroLote;

	return (
		<div
			className={`bg-[var(--cor-painel)] border rounded-xl p-4 ${
				rascunho.salva
					? "border-[var(--cor-acerto)]/40"
					: "border-[var(--cor-borda)]"
			}`}
		>
			<div className="flex items-center gap-2 mb-3 flex-wrap">
				<span className="font-bold text-[var(--cor-destaque)]">
					Questao {rascunho.numero}
				</span>
				{rascunho.pagina && (
					<button
						type="button"
						onClick={() => onPaginaClick(rascunho.pagina)}
						className="text-xs bg-black/30 px-2 py-0.5 rounded hover:bg-black/50 cursor-pointer"
					>
						Ver pagina {rascunho.pagina}
					</button>
				)}
				{rascunho.alternativas_incompletas && !rascunho.sem_texto && (
					<span className="text-xs bg-amber-900/40 text-amber-300 px-2 py-0.5 rounded">
						Revisar — faltam alternativas
					</span>
				)}
				{rascunho.sem_texto && !rascunho.salva && (
					<span className="text-xs bg-red-900/40 text-red-300 px-2 py-0.5 rounded">
						Texto nao extraido (pagina em duas colunas) — digite manualmente ou
						descarte
					</span>
				)}
				{rascunho.mistura_possivel &&
					!rascunho.salva &&
					!rascunho.sem_texto && (
						<span className="text-xs bg-amber-900/40 text-amber-300 px-2 py-0.5 rounded">
							Pode conter texto da questao seguinte (duas colunas) — confira o
							texto antes de salvar
						</span>
					)}
				{rascunho.existenteId && !rascunho.salva && (
					<span className="text-xs bg-sky-900/40 text-sky-300 px-2 py-0.5 rounded">
						Ja existe no banco: {rascunho.existenteRotulo}
					</span>
				)}
				{rascunho.salva && (
					<span className="text-xs bg-[var(--cor-acerto)]/20 text-[var(--cor-acerto)] px-2 py-0.5 rounded font-bold">
						{ROTULO_RESULTADO[rascunho.resultado] ?? "✓ Salva"}
					</span>
				)}
			</div>

			<fieldset
				disabled={rascunho.salva}
				className="space-y-3 disabled:opacity-50"
			>
				<textarea
					value={rascunho.enunciado}
					onChange={(e) => atualizar({ enunciado: e.target.value })}
					rows={3}
					className={CAMPO_CLASS}
					placeholder="Enunciado..."
				/>

				{LETRAS.map((letra) => (
					<div key={letra} className="flex items-center gap-2">
						<span className="w-5 text-xs text-gray-400 uppercase">{letra}</span>
						<input
							type="text"
							value={rascunho[`alternativa_${letra}`]}
							onChange={(e) =>
								atualizar({ [`alternativa_${letra}`]: e.target.value })
							}
							className={CAMPO_CLASS}
						/>
					</div>
				))}

				<div className="grid grid-cols-2 md:grid-cols-5 gap-3">
					<select
						value={rascunho.tipo}
						onChange={(e) => atualizar({ tipo: e.target.value })}
						className={CAMPO_CLASS}
					>
						<option value="CE">Comp. Especifico</option>
						<option value="FG">Formacao Geral</option>
					</select>
					<select
						value={rascunho.resposta}
						onChange={(e) => atualizar({ resposta: e.target.value })}
						className={CAMPO_CLASS}
					>
						{["A", "B", "C", "D", "E"].map((l) => (
							<option key={l} value={l}>
								Resposta {l}
							</option>
						))}
					</select>
					<select
						value={rascunho.dificuldade}
						onChange={(e) => atualizar({ dificuldade: e.target.value })}
						className={CAMPO_CLASS}
					>
						<option value="facil">Facil</option>
						<option value="medio">Medio</option>
						<option value="dificil">Dificil</option>
					</select>
					<input
						type="text"
						value={rascunho.assunto}
						onChange={(e) => atualizar({ assunto: e.target.value })}
						placeholder="Assunto"
						className={CAMPO_CLASS}
					/>
					<input
						type="text"
						value={rascunho.fonte || ""}
						onChange={(e) => atualizar({ fonte: e.target.value })}
						placeholder="Fonte / nome da prova"
						className={CAMPO_CLASS}
					/>
				</div>

				<div>
					{rascunho.imagem ? (
						<div className="flex items-center gap-3">
							<img
								src={rascunho.imagem}
								alt="Imagem anexada a questao"
								className="max-h-24 rounded border border-[var(--cor-borda)]"
							/>
							<button
								type="button"
								onClick={() => atualizar({ imagem: null })}
								className="text-red-400 text-xs cursor-pointer hover:text-red-300"
							>
								Remover imagem
							</button>
						</div>
					) : (
						<input
							type="file"
							accept="image/*"
							onChange={handleImagem}
							className="text-xs text-gray-400"
						/>
					)}
				</div>
			</fieldset>

			{mensagemErro && (
				<p className="text-red-400 text-xs mt-2">{mensagemErro}</p>
			)}

			{!rascunho.salva && (
				<div className="flex gap-3 mt-3">
					<button
						type="button"
						onClick={salvar}
						disabled={enviando || !salvavelAgora}
						className="bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold text-sm px-4 py-1.5 rounded-lg hover:brightness-110 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
					>
						{enviando
							? "Salvando..."
							: apenasAnexar
								? "Anexar pagina ao existente"
								: "Salvar questao"}
					</button>
					<button
						type="button"
						onClick={() => atualizar({ descartada: true })}
						className="text-gray-400 text-sm cursor-pointer hover:text-gray-300"
					>
						Descartar
					</button>
				</div>
			)}
		</div>
	);
}

export default function ImportarPdfPage({ onFechar }) {
	const [arquivo, setArquivo] = useState(null);
	const [ano, setAno] = useState(new Date().getFullYear());
	const [inicioCE, setInicioCE] = useState(1);
	const [fonte, setFonte] = useState("");
	const [carregando, setCarregando] = useState(false);
	const [erro, setErro] = useState(null);
	const [paginas, setPaginas] = useState([]);
	const [rascunhos, setRascunhos] = useState(null);
	const [paginaAberta, setPaginaAberta] = useState(null);
	const [anexarPaginas, setAnexarPaginas] = useState(true);
	const [anexarSeExistir, setAnexarSeExistir] = useState(true);
	const [salvandoTodas, setSalvandoTodas] = useState(false);
	const [mensagemLote, setMensagemLote] = useState(null);
	const [classificando, setClassificando] = useState(false);
	const [progressoIA, setProgressoIA] = useState("");
	const [erroIA, setErroIA] = useState(null);
	const [iaStatus, setIaStatus] = useState(null);
	const [testeIA, setTesteIA] = useState(null);
	const [testando, setTestando] = useState(false);

	useEffect(() => {
		statusIA()
			.then(setIaStatus)
			.catch(() => setIaStatus(null));
	}, []);

	async function handleTestarIA() {
		setTestando(true);
		setTesteIA(null);
		try {
			const status = await statusIA(true);
			setIaStatus(status);
			setTesteIA(
				status.teste?.ok
					? "Conexao com o Gemini OK."
					: status.teste?.erro || "A IA nao esta configurada.",
			);
		} catch (err) {
			setTesteIA(err.message);
		} finally {
			setTestando(false);
		}
	}

	async function handleImportar(e) {
		e.preventDefault();
		if (!arquivo) return;
		setCarregando(true);
		setErro(null);
		setMensagemLote(null);
		setErroIA(null);
		try {
			const resultado = await importarPdf(arquivo, ano, inicioCE);

			// Descobre quais questoes ja existem (mesmo ano e numero) para nao
			// criar duplicatas e poder so anexar a pagina original a elas.
			let existentes = [];
			try {
				existentes = await listarQuestoes({ ano });
			} catch {
				existentes = [];
			}
			const porNumero = new Map(existentes.map((q) => [q.numero, q]));

			setPaginas(resultado.paginas);
			setRascunhos(
				resultado.questoes.map((q) => {
					const existente = porNumero.get(q.numero);
					return {
						...q,
						fonte,
						imagem: null,
						salva: false,
						descartada: false,
						resultado: null,
						erroLote: null,
						existenteId: existente?.id ?? null,
						existenteRotulo: existente
							? `${existente.fonte || `ENADE ${existente.ano}`} Q${existente.numero}`
							: null,
					};
				}),
			);
		} catch (err) {
			setErro(err.message);
		} finally {
			setCarregando(false);
		}
	}

	function atualizarRascunho(indice, mudancas) {
		setRascunhos((anterior) =>
			anterior.map((r, i) => (i === indice ? { ...r, ...mudancas } : r)),
		);
	}

	function paginaImagemDe(r) {
		if (!anexarPaginas || !r.pagina) return null;
		return paginas[r.pagina - 1] ?? null;
	}

	function indicesPendentes() {
		return rascunhos
			.map((r, i) => (!r.salva && !r.descartada ? i : null))
			.filter((i) => i !== null);
	}

	async function handleSalvarTodas() {
		const pendentesIdx = indicesPendentes();
		const elegiveis = pendentesIdx.filter((i) =>
			elegivelParaLote(
				rascunhos[i],
				paginaImagemDe(rascunhos[i]),
				anexarSeExistir,
			),
		);
		const puladas = pendentesIdx.length - elegiveis.length;
		const contagem = { criada: 0, atualizada: 0, ignorada: 0 };

		if (elegiveis.length === 0) {
			setMensagemLote({ contagem, erros: [], puladas, abortado: false });
			return;
		}
		if (
			!confirm(
				`Salvar ${elegiveis.length} questao(es) de uma vez?` +
					(puladas > 0
						? ` ${puladas} serao puladas por precisarem de revisao manual.`
						: ""),
			)
		) {
			return;
		}

		setSalvandoTodas(true);
		setMensagemLote(null);
		const erros = [];
		let falhasDeRedeSeguidas = 0;
		let abortado = false;
		for (const i of elegiveis) {
			const r = rascunhos[i];
			try {
				const resultado = await persistirRascunho(
					r,
					paginaImagemDe(r),
					anexarSeExistir,
				);
				contagem[resultado] += 1;
				falhasDeRedeSeguidas = 0;
				atualizarRascunho(i, { salva: true, resultado, erroLote: null });
			} catch (err) {
				erros.push(`Q${r.numero}: ${err.message}`);
				atualizarRascunho(i, { erroLote: err.message });
				falhasDeRedeSeguidas = err.rede ? falhasDeRedeSeguidas + 1 : 0;
				if (falhasDeRedeSeguidas >= FALHAS_DE_REDE_PARA_INTERROMPER) {
					abortado = true;
					break;
				}
			}
		}
		setSalvandoTodas(false);
		setMensagemLote({ contagem, erros, puladas, abortado });
	}

	async function handleClassificarTodas() {
		// So classifica o que tem texto: questao vazia nao tem o que classificar.
		const indices = indicesPendentes().filter((i) =>
			textoCompleto(rascunhos[i]),
		);
		if (indices.length === 0) return;
		setClassificando(true);
		setErroIA(null);
		let feitas = 0;
		setProgressoIA(`0/${indices.length}`);
		for (let inicio = 0; inicio < indices.length; inicio += TAMANHO_LOTE_IA) {
			const grupo = indices.slice(inicio, inicio + TAMANHO_LOTE_IA);
			try {
				const { resultados } = await classificarQuestoesLote(
					grupo.map((i) => camposParaIA(rascunhos[i])),
				);
				resultados.forEach((res, pos) => {
					const atual = rascunhos[grupo[pos]];
					atualizarRascunho(grupo[pos], {
						assunto: res.assunto || atual.assunto,
						dificuldade: res.dificuldade || atual.dificuldade,
					});
				});
				feitas += grupo.length;
				setProgressoIA(`${feitas}/${indices.length}`);
			} catch (err) {
				setErroIA(
					`${err.message} (classificadas ${feitas} de ${indices.length})`,
				);
				break;
			}
		}
		setClassificando(false);
	}

	const pendentes = rascunhos?.filter((r) => !r.salva && !r.descartada) ?? [];
	const elegiveisLote = pendentes.filter((r) =>
		elegivelParaLote(r, paginaImagemDe(r), anexarSeExistir),
	).length;
	const precisamRevisao = pendentes.length - elegiveisLote;
	const salvas = rascunhos?.filter((r) => r.salva).length ?? 0;

	return (
		<div className="bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-xl p-6 mb-6">
			<div className="flex items-center justify-between mb-4">
				<h2 className="text-lg font-bold">Importar questoes de um PDF</h2>
				<button
					type="button"
					onClick={onFechar}
					className="text-gray-400 text-sm cursor-pointer hover:text-gray-300"
				>
					Fechar
				</button>
			</div>

			{iaStatus && (
				<div
					className={`text-xs rounded-lg px-3 py-2 mb-4 flex flex-wrap items-center gap-3 border ${
						iaStatus.configurada
							? "bg-emerald-900/20 border-emerald-500/30 text-emerald-200"
							: "bg-amber-900/20 border-amber-500/30 text-amber-200"
					}`}
				>
					<span>
						{iaStatus.configurada
							? `IA (Gemini) configurada — modelo ${iaStatus.modelo}`
							: "IA (Gemini) NAO configurada: coloque GEMINI_API_KEY no arquivo .env e rode docker compose up -d --build."}
					</span>
					{iaStatus.configurada && (
						<button
							type="button"
							onClick={handleTestarIA}
							disabled={testando}
							className="underline cursor-pointer disabled:opacity-50"
						>
							{testando ? "Testando..." : "Testar conexao"}
						</button>
					)}
					{testeIA && <span className="font-bold">{testeIA}</span>}
				</div>
			)}

			{!rascunhos && (
				<form onSubmit={handleImportar} className="space-y-4">
					<p className="text-sm text-gray-400">
						Envie o PDF de uma prova (ENADE ou similar). O texto e o gabarito
						sao extraidos automaticamente; voce revisa, edita e anexa imagens
						antes de salvar cada questao.
					</p>
					<div>
						<label htmlFor="arquivo-pdf" className="block text-sm mb-1">
							Arquivo PDF
						</label>
						<input
							id="arquivo-pdf"
							type="file"
							accept="application/pdf"
							onChange={(e) => setArquivo(e.target.files?.[0] ?? null)}
							required
							className="text-sm"
						/>
					</div>
					<div>
						<label htmlFor="fonte-prova" className="block text-sm mb-1">
							Nome da prova ou lista
						</label>
						<input
							id="fonte-prova"
							type="text"
							value={fonte}
							onChange={(e) => setFonte(e.target.value)}
							placeholder="Ex: Lista de Algoritmos - Prof. Fulano, ENADE 2019, Prova C216..."
							className={CAMPO_CLASS}
						/>
						<p className="text-xs text-gray-500 mt-1">
							Deixe em branco para usar "ENADE {ano}" automaticamente. Esse nome
							aparece no simulado em vez do ano.
						</p>
					</div>
					<div className="grid grid-cols-2 gap-4">
						<div>
							<label htmlFor="ano-prova" className="block text-sm mb-1">
								Ano / identificador numerico
							</label>
							<input
								id="ano-prova"
								type="number"
								value={ano}
								onChange={(e) => setAno(Number(e.target.value))}
								className={CAMPO_CLASS}
							/>
							<p className="text-xs text-gray-500 mt-1">
								Pode ser o ano do curso se nao for uma prova oficial. Questoes
								com o mesmo ano e numero sao tratadas como a mesma questao.
							</p>
						</div>
						<div>
							<label htmlFor="inicio-ce" className="block text-sm mb-1">
								Numero da 1a questao do Componente Especifico
							</label>
							<input
								id="inicio-ce"
								type="number"
								value={inicioCE}
								onChange={(e) => setInicioCE(Number(e.target.value))}
								className={CAMPO_CLASS}
							/>
							<p className="text-xs text-gray-500 mt-1">
								Questoes antes desse numero (Formacao Geral) nao sao importadas.
								No ENADE 2023 de Engenharia de Computacao, use 10.
							</p>
						</div>
					</div>
					{erro && <p className="text-red-400 text-sm">{erro}</p>}
					<button
						type="submit"
						disabled={carregando || !arquivo}
						className="bg-[var(--cor-destaque)] text-[var(--cor-fundo)] font-bold px-6 py-2 rounded-lg hover:brightness-110 transition cursor-pointer disabled:opacity-50"
					>
						{carregando ? "Processando PDF..." : "Importar"}
					</button>
				</form>
			)}

			{rascunhos && (
				<div>
					<div className="flex items-center justify-between mb-3 flex-wrap gap-3">
						<p className="text-sm text-gray-400">
							{pendentes.length} pendente(s) de revisao, {salvas} salva(s)
						</p>
						<div className="flex gap-2 flex-wrap">
							<button
								type="button"
								onClick={handleClassificarTodas}
								disabled={
									classificando || salvandoTodas || pendentes.length === 0
								}
								className="bg-emerald-700/50 border border-emerald-500/40 text-emerald-200 text-xs font-bold px-4 py-1.5 rounded-lg hover:bg-emerald-700/70 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
							>
								{classificando
									? `Classificando ${progressoIA}...`
									: "Classificar via IA (assunto + dificuldade)"}
							</button>
							<button
								type="button"
								onClick={handleSalvarTodas}
								disabled={
									salvandoTodas || classificando || pendentes.length === 0
								}
								className="bg-[var(--cor-destaque)] text-[var(--cor-fundo)] text-xs font-bold px-4 py-1.5 rounded-lg hover:brightness-110 cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
							>
								{salvandoTodas
									? "Salvando..."
									: `Salvar todas (${elegiveisLote})`}
							</button>
							<button
								type="button"
								onClick={() => {
									setRascunhos(null);
									setPaginas([]);
									setMensagemLote(null);
									setErroIA(null);
								}}
								className="text-xs text-gray-400 hover:text-gray-300 cursor-pointer"
							>
								Importar outro PDF
							</button>
						</div>
					</div>

					{precisamRevisao > 0 && (
						<p className="text-xs text-amber-300 mb-3">
							{precisamRevisao} questao(es) precisam de revisao manual (texto
							nao extraido ou possivel mistura de colunas) e nao entram no
							"Salvar todas". Revise e salve uma a uma.
						</p>
					)}

					<div className="flex flex-col gap-1 mb-4">
						<label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
							<input
								type="checkbox"
								checked={anexarPaginas}
								onChange={(e) => setAnexarPaginas(e.target.checked)}
								className="accent-[var(--cor-destaque)]"
							/>
							Anexar a pagina original do PDF em cada questao (botao "Ver pagina
							do PDF" no simulado)
						</label>
						<label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
							<input
								type="checkbox"
								checked={anexarSeExistir}
								onChange={(e) => setAnexarSeExistir(e.target.checked)}
								className="accent-[var(--cor-destaque)]"
							/>
							Se a questao ja existir (mesmo ano e numero), so anexar a pagina —
							nao criar duplicata
						</label>
					</div>

					{erroIA && (
						<p
							role="alert"
							className="text-sm rounded-lg px-4 py-3 mb-4 bg-red-900/30 border border-red-500/50 text-red-300"
						>
							{erroIA}
						</p>
					)}

					{mensagemLote && (
						<div className="text-sm rounded-lg px-4 py-3 mb-4 bg-black/20 border border-[var(--cor-borda)]">
							<p>{textoResumo(mensagemLote)}</p>
							{mensagemLote.erros.slice(0, 3).map((e) => (
								<p key={e} className="text-red-400 text-xs mt-1">
									{e}
								</p>
							))}
						</div>
					)}

					{paginas.length > 0 && (
						<details className="mb-4">
							<summary className="text-sm text-cyan-300 cursor-pointer">
								Ver paginas do PDF ({paginas.length})
							</summary>
							<div className="grid grid-cols-6 md:grid-cols-10 gap-2 mt-3">
								{paginas.map((src, i) => (
									<button
										key={`pagina-${i + 1}`}
										type="button"
										onClick={() => setPaginaAberta(i + 1)}
										className="relative border border-[var(--cor-borda)] rounded overflow-hidden hover:border-[var(--cor-destaque)] cursor-pointer"
									>
										<img src={src} alt={`Pagina ${i + 1}`} className="w-full" />
										<span className="absolute bottom-0 right-0 bg-black/70 text-xs px-1">
											{i + 1}
										</span>
									</button>
								))}
							</div>
						</details>
					)}

					{paginaAberta && (
						<button
							type="button"
							onClick={() => setPaginaAberta(null)}
							className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-6 cursor-zoom-out"
						>
							<img
								src={paginas[paginaAberta - 1]}
								alt={`Pagina ${paginaAberta} ampliada`}
								className="max-h-full max-w-full rounded-lg"
							/>
						</button>
					)}

					<div className="space-y-4">
						{rascunhos.map((rascunho, i) => (
							<RascunhoCard
								key={`${rascunho.ano}-${rascunho.numero}`}
								rascunho={rascunho}
								atualizar={(mudancas) => atualizarRascunho(i, mudancas)}
								onPaginaClick={setPaginaAberta}
								anexarSeExistir={anexarSeExistir}
								paginaImagem={paginaImagemDe(rascunho)}
							/>
						))}
					</div>
				</div>
			)}
		</div>
	);
}
