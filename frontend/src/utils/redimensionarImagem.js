/**
 * Le um arquivo de imagem, redimensiona (largura maxima) e comprime em
 * JPEG, devolvendo uma data URI base64 pronta para salvar no banco. Isso
 * evita gravar fotos/prints gigantes direto no Postgres.
 */
export function redimensionarImagem(
	arquivo,
	larguraMaxima = 900,
	qualidade = 0.82,
) {
	return new Promise((resolve, reject) => {
		const leitor = new FileReader();
		leitor.onerror = () => reject(new Error("Nao foi possivel ler o arquivo."));
		leitor.onload = () => {
			const imagem = new Image();
			imagem.onerror = () => reject(new Error("Arquivo de imagem invalido."));
			imagem.onload = () => {
				const escala = Math.min(1, larguraMaxima / imagem.width);
				const canvas = document.createElement("canvas");
				canvas.width = Math.round(imagem.width * escala);
				canvas.height = Math.round(imagem.height * escala);
				const ctx = canvas.getContext("2d");
				ctx.drawImage(imagem, 0, 0, canvas.width, canvas.height);
				resolve(canvas.toDataURL("image/jpeg", qualidade));
			};
			imagem.src = leitor.result;
		};
		leitor.readAsDataURL(arquivo);
	});
}
