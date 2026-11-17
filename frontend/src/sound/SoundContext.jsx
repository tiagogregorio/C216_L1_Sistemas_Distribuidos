import { createContext, useContext, useEffect, useRef, useState } from "react";
import * as soundEngine from "./soundEngine";

const ENABLED_KEY = "enade:sound-enabled";
const VOLUME_KEY = "enade:music-volume";
const MUSICA_SRC = "/audio/musica-fundo.mp3";

const SoundContext = createContext(null);

export function SoundProvider({ children }) {
	const [enabled, setEnabled] = useState(() => {
		const salvo = localStorage.getItem(ENABLED_KEY);
		return salvo === null ? true : salvo === "true";
	});
	const [volume, setVolume] = useState(() => {
		const salvo = localStorage.getItem(VOLUME_KEY);
		return salvo === null ? 0.5 : Number(salvo);
	});
	const [musicaDesejada, setMusicaDesejada] = useState(false);
	const [arquivoDisponivel, setArquivoDisponivel] = useState(true);
	const audioRef = useRef(null);

	useEffect(() => {
		localStorage.setItem(ENABLED_KEY, String(enabled));
	}, [enabled]);

	useEffect(() => {
		localStorage.setItem(VOLUME_KEY, String(volume));
		if (audioRef.current) {
			audioRef.current.volume = volume;
		}
	}, [volume]);

	useEffect(() => {
		const audio = audioRef.current;
		if (!audio) return;

		if (!musicaDesejada) {
			audio.pause();
			return;
		}

		const tentarTocar = () => audio.play().catch(() => {});
		tentarTocar();

		// Logo apos um F5, o navegador bloqueia play() automatico ate que o
		// usuario interaja com a pagina (politica de autoplay). Se isso
		// aconteceu, a primeira interacao (clique ou tecla) tenta de novo.
		function retomarSeNecessario() {
			if (audio.paused) tentarTocar();
		}
		document.addEventListener("click", retomarSeNecessario, { once: true });
		document.addEventListener("keydown", retomarSeNecessario, {
			once: true,
		});

		return () => {
			document.removeEventListener("click", retomarSeNecessario);
			document.removeEventListener("keydown", retomarSeNecessario);
		};
	}, [musicaDesejada]);

	function toggle() {
		setEnabled((atual) => !atual);
	}

	function comSom(fn) {
		return (...args) => {
			if (enabled) fn(...args);
		};
	}

	const value = {
		enabled,
		toggle,
		volume,
		setVolume,
		arquivoDisponivel,
		playSelect: comSom(soundEngine.playSelect),
		playCorrect: comSom(soundEngine.playCorrect),
		playWrong: comSom(soundEngine.playWrong),
		playHelp: comSom(soundEngine.playHelp),
		/** Chamado por uma pagina para pedir (true) ou liberar (false) a musica de fundo. */
		setMusicaAtiva: setMusicaDesejada,
	};

	return (
		<SoundContext.Provider value={value}>
			{children}
			{/* biome-ignore lint/a11y/useMediaCaption: trilha instrumental de fundo, decorativa */}
			<audio
				ref={audioRef}
				src={MUSICA_SRC}
				loop
				preload="auto"
				onError={() => setArquivoDisponivel(false)}
				onCanPlay={() => setArquivoDisponivel(true)}
			/>
		</SoundContext.Provider>
	);
}

export function useSound() {
	const ctx = useContext(SoundContext);
	if (!ctx) {
		throw new Error("useSound deve ser usado dentro de um SoundProvider");
	}
	return ctx;
}
