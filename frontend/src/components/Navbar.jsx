export default function Navbar({ pagina, setPagina }) {
	const itens = [
		{ id: "questoes", label: "Questoes" },
		{ id: "novo-simulado", label: "Novo Simulado" },
		{ id: "historico", label: "Historico" },
		{ id: "dashboard", label: "Dashboard" },
		{ id: "relatorio", label: "Relatorio" },
	];

	return (
		<nav className="bg-[var(--cor-painel)] border-b border-[var(--cor-borda)] px-6 py-3">
			<div className="max-w-6xl mx-auto flex items-center justify-between">
				<button
					type="button"
					onClick={() => setPagina("dashboard")}
					className="text-[var(--cor-destaque)] font-bold text-xl tracking-wide cursor-pointer"
				>
					ENADE Study Platform
				</button>
				<div className="flex gap-1">
					{itens.map((item) => (
						<button
							key={item.id}
							type="button"
							onClick={() => setPagina(item.id)}
							className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
								pagina === item.id
									? "bg-[var(--cor-destaque)] text-[var(--cor-fundo)]"
									: "text-[var(--cor-texto)] hover:bg-[var(--cor-borda)]"
							}`}
						>
							{item.label}
						</button>
					))}
				</div>
			</div>
		</nav>
	);
}
