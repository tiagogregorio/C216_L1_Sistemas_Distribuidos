export const TITULO_MIN = 3;
export const TITULO_MAX = 80;
export const PRIORIDADES = ["baixa", "media", "alta"];
export const STATUS_OPTIONS = ["pendente", "concluida"];

export function validateTarefa({ titulo, prioridade }) {
  const errors = {};
  const trimmed = titulo.trim();

  if (!trimmed) {
    errors.titulo = "O título é obrigatório.";
  } else if (trimmed.length < TITULO_MIN) {
    errors.titulo = `O título deve ter no mínimo ${TITULO_MIN} caracteres.`;
  } else if (trimmed.length > TITULO_MAX) {
    errors.titulo = `O título deve ter no máximo ${TITULO_MAX} caracteres.`;
  }

  if (!PRIORIDADES.includes(prioridade)) {
    errors.prioridade = "Prioridade inválida.";
  }

  return { errors, values: { titulo: trimmed, prioridade } };
}
