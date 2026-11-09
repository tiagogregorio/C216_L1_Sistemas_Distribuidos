import { useEffect, useState } from "react";
import Navbar from "./components/Navbar";
import SoundToggle from "./components/SoundToggle";
import DashboardPage from "./pages/DashboardPage";
import HistoricoPage from "./pages/HistoricoPage";
import NovoSimuladoPage from "./pages/NovoSimuladoPage";
import QuestoesPage from "./pages/QuestoesPage";
import RelatorioPage from "./pages/RelatorioPage";
import SimuladoPage from "./pages/SimuladoPage";
import { SoundProvider } from "./sound/SoundContext";
import { limparProgresso } from "./utils/progressoSimulado";

const PAGINA_KEY = "enade:pagina-atual";
const SIMULADO_ATIVO_KEY = "enade:simulado-ativo";

function lerSimuladoAtivoSalvo() {
	try {
		const bruto = localStorage.getItem(SIMULADO_ATIVO_KEY);
		return bruto ? JSON.parse(bruto) : null;
	} catch {
		return null;
	}
}

export default function App() {
	const [simuladoAtivo, setSimuladoAtivo] = useState(() =>
		lerSimuladoAtivoSalvo(),
	);
	const [pagina, setPagina] = useState(() => {
		const salva = localStorage.getItem(PAGINA_KEY);
		// So volta direto para a tela do simulado se de fato houver um
		// simulado salvo para retomar; caso contrario, cai no dashboard.
		if (salva === "simulado" && !lerSimuladoAtivoSalvo()) {
			return "dashboard";
		}
		return salva || "dashboard";
	});

	useEffect(() => {
		localStorage.setItem(PAGINA_KEY, pagina);
	}, [pagina]);

	useEffect(() => {
		if (simuladoAtivo) {
			localStorage.setItem(SIMULADO_ATIVO_KEY, JSON.stringify(simuladoAtivo));
		} else {
			localStorage.removeItem(SIMULADO_ATIVO_KEY);
		}
	}, [simuladoAtivo]);

	function iniciarSimulado(simuladoId, questaoIds) {
		setSimuladoAtivo({ simuladoId, questaoIds });
		setPagina("simulado");
	}

	function voltarDoSimulado() {
		if (simuladoAtivo) limparProgresso(simuladoAtivo.simuladoId);
		setSimuladoAtivo(null);
		setPagina("historico");
	}

	function pararSimulado() {
		// Nao limpa o progresso salvo: "Parar" so sai da tela agora, o
		// simulado continua "Em andamento" no Historico para ser retomado
		// depois de onde o usuario parou.
		setSimuladoAtivo(null);
		setPagina("dashboard");
	}

	return (
		<SoundProvider>
			<div className="min-h-screen">
				{pagina !== "simulado" && (
					<Navbar pagina={pagina} setPagina={setPagina} />
				)}
				<main>
					{pagina === "dashboard" && <DashboardPage />}
					{pagina === "questoes" && <QuestoesPage />}
					{pagina === "novo-simulado" && (
						<NovoSimuladoPage onIniciar={iniciarSimulado} />
					)}
					{pagina === "simulado" && simuladoAtivo && (
						<SimuladoPage
							simuladoId={simuladoAtivo.simuladoId}
							questaoIds={simuladoAtivo.questaoIds}
							onVoltar={voltarDoSimulado}
							onParar={pararSimulado}
						/>
					)}
					{pagina === "historico" && (
						<HistoricoPage onContinuar={iniciarSimulado} />
					)}
					{pagina === "relatorio" && <RelatorioPage />}
				</main>
				<SoundToggle />
			</div>
		</SoundProvider>
	);
}
