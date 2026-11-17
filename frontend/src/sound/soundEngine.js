/**
 * Motor de efeitos sonoros 100% sintetizado via Web Audio API.
 *
 * Nenhum arquivo de audio e usado ou distribuido aqui — todo som e gerado
 * em tempo real por osciladores (sem nenhuma ligacao com audios protegidos
 * por direitos autorais de terceiros).
 *
 * A musica de fundo NAO fica aqui: ela e um arquivo .mp3 escolhido pelo
 * proprio usuario, tocado via elemento <audio> (ver sound/SoundContext.jsx).
 */

let audioCtx = null;

function getContext() {
	if (!audioCtx) {
		const AudioContextClass = window.AudioContext || window.webkitAudioContext;
		audioCtx = new AudioContextClass();
	}
	if (audioCtx.state === "suspended") {
		audioCtx.resume();
	}
	return audioCtx;
}

/**
 * Toca uma nota simples com envelope de volume (ataque curto + decaimento),
 * evitando estalos (clicks) no inicio/fim do som.
 */
function playTone({
	frequency,
	duration = 0.15,
	type = "sine",
	volume = 0.2,
	delay = 0,
}) {
	const ctx = getContext();
	const startTime = ctx.currentTime + delay;

	const oscillator = ctx.createOscillator();
	oscillator.type = type;
	oscillator.frequency.setValueAtTime(frequency, startTime);

	const gain = ctx.createGain();
	gain.gain.setValueAtTime(0, startTime);
	gain.gain.linearRampToValueAtTime(volume, startTime + 0.01);
	gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

	oscillator.connect(gain);
	gain.connect(ctx.destination);

	oscillator.start(startTime);
	oscillator.stop(startTime + duration + 0.02);
}

/** Clique suave ao selecionar uma alternativa. */
export function playSelect() {
	playTone({ frequency: 440, duration: 0.07, type: "sine", volume: 0.12 });
}

/** Arpejo ascendente e triunfante para resposta certa. */
export function playCorrect() {
	const notas = [523.25, 659.25, 783.99, 1046.5]; // C5 E5 G5 C6
	notas.forEach((freq, i) => {
		playTone({
			frequency: freq,
			duration: 0.18,
			type: "triangle",
			volume: 0.18,
			delay: i * 0.09,
		});
	});
}

/** Som grave descendente para resposta errada. */
export function playWrong() {
	playTone({ frequency: 220, duration: 0.25, type: "sawtooth", volume: 0.15 });
	playTone({
		frequency: 164.81,
		duration: 0.35,
		type: "sawtooth",
		volume: 0.15,
		delay: 0.12,
	});
}

/** Efeito curto para abrir/usar um icone de ajuda. */
export function playHelp() {
	playTone({ frequency: 659.25, duration: 0.1, type: "sine", volume: 0.15 });
	playTone({
		frequency: 880,
		duration: 0.15,
		type: "sine",
		volume: 0.15,
		delay: 0.1,
	});
}
