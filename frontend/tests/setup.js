import "@testing-library/jest-dom";

// jsdom nao implementa Web Audio API; mock minimo para os componentes que
// usam efeitos sonoros (frontend/src/sound/) nao quebrarem nos testes.
class AudioContextMock {
	constructor() {
		this.state = "running";
		this.currentTime = 0;
		this.destination = {};
	}
	createOscillator() {
		return {
			type: "sine",
			frequency: { setValueAtTime: () => {} },
			connect: () => {},
			start: () => {},
			stop: () => {},
		};
	}
	createGain() {
		return {
			gain: {
				setValueAtTime: () => {},
				linearRampToValueAtTime: () => {},
				exponentialRampToValueAtTime: () => {},
				cancelScheduledValues: () => {},
				value: 0,
			},
			connect: () => {},
		};
	}
	resume() {}
}

window.AudioContext = AudioContextMock;
