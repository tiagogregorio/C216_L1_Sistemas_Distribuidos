import { useState } from "react";
import Navbar from "./components/Navbar";
import QuestoesPage from "./pages/QuestoesPage";
import NovoSimuladoPage from "./pages/NovoSimuladoPage";
import SimuladoPage from "./pages/SimuladoPage";
import HistoricoPage from "./pages/HistoricoPage";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
	const [pagina, setPagina] = useState("dashboard");
	const [simuladoAtivo, setSimuladoAtivo] = useState(null);

	function iniciarSimulado(simuladoId, questaoIds) {
		setSimuladoAtivo({ simuladoId, questaoIds });
		setPagina("simulado");
	}

	function voltarDoSimulado() {
		setSimuladoAtivo(null);
		setPagina("historico");
	}

	return (
		<div className="min-h-screen">
			{pagina !== "simulado" && <Navbar pagina={pagina} setPagina={setPagina} />}
			<main>
				{pagina === "dashboard" && <DashboardPage />}
				{pagina === "questoes" && <QuestoesPage />}
				{pagina === "novo-simulado" && <NovoSimuladoPage onIniciar={iniciarSimulado} />}
				{pagina === "simulado" && simuladoAtivo && (
					<SimuladoPage
						simuladoId={simuladoAtivo.simuladoId}
						questaoIds={simuladoAtivo.questaoIds}
						onVoltar={voltarDoSimulado}
					/>
				)}
				{pagina === "historico" && <HistoricoPage />}
			</main>
		</div>
	);
}
