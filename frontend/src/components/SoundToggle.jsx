import { useSound } from "../sound/SoundContext";

export default function SoundToggle() {
	const { enabled, toggle, volume, setVolume, arquivoDisponivel } = useSound();

	return (
		<div className="fixed bottom-5 right-5 z-50 flex items-center gap-3 bg-[var(--cor-painel)] border border-[var(--cor-borda)] rounded-full shadow-lg pl-4 pr-2 py-2">
			{!arquivoDisponivel && (
				<span
					className="text-amber-400 text-xs"
					title={
						"Arquivo de musica nao encontrado. Coloque um .mp3 em " +
						"frontend/public/audio/musica-fundo.mp3"
					}
				>
					⚠
				</span>
			)}

			<svg
				viewBox="0 0 24 24"
				className="w-4 h-4 text-gray-400 shrink-0"
				fill="currentColor"
				aria-hidden="true"
			>
				<title>Volume da musica de fundo</title>
				<path d="M9 18V5l12-2v13" />
				<circle cx="6" cy="18" r="3" />
				<circle cx="18" cy="16" r="3" />
			</svg>
			<input
				type="range"
				min="0"
				max="1"
				step="0.05"
				value={volume}
				onChange={(e) => setVolume(Number(e.target.value))}
				aria-label="Volume da musica de fundo"
				className="w-24 accent-[var(--cor-destaque)] cursor-pointer"
			/>

			<button
				type="button"
				onClick={toggle}
				aria-label={
					enabled ? "Desligar efeitos sonoros" : "Ligar efeitos sonoros"
				}
				title={
					enabled ? "Efeitos sonoros ligados" : "Efeitos sonoros desligados"
				}
				className="w-9 h-9 rounded-full flex items-center justify-center cursor-pointer hover:bg-[var(--cor-borda)] transition-colors shrink-0"
			>
				{enabled ? (
					<svg
						viewBox="0 0 24 24"
						className="w-5 h-5 text-[var(--cor-destaque)]"
						fill="currentColor"
						aria-hidden="true"
					>
						<title>Efeitos sonoros ligados</title>
						<path d="M3 10v4h4l5 5V5L7 10H3z" />
						<path
							d="M16.5 12a4.5 4.5 0 0 0-2.5-4.03v8.06A4.5 4.5 0 0 0 16.5 12z"
							stroke="currentColor"
							strokeWidth="1.5"
							fill="none"
						/>
						<path
							d="M18.5 7.5a8 8 0 0 1 0 9"
							stroke="currentColor"
							strokeWidth="1.5"
							fill="none"
							strokeLinecap="round"
						/>
					</svg>
				) : (
					<svg
						viewBox="0 0 24 24"
						className="w-5 h-5 text-gray-500"
						fill="currentColor"
						aria-hidden="true"
					>
						<title>Efeitos sonoros desligados</title>
						<path d="M3 10v4h4l5 5V5L7 10H3z" />
						<path
							d="M16 9l5 6M21 9l-5 6"
							stroke="currentColor"
							strokeWidth="1.8"
							strokeLinecap="round"
						/>
					</svg>
				)}
			</button>
		</div>
	);
}
