"""Regras de negocio dos simulados. Nao conhece HTTP nem SQL."""

from app.models.simulado import Simulado
from app.repositories.questao import QuestaoRepository
from app.repositories.simulado import SimuladoRepository
from app.schemas.simulado import SimuladoCreate, SimuladoSubmit


class SimuladoNaoEncontradoError(Exception):
    """Levantada quando o simulado informado nao existe."""


class SimuladoJaFinalizadoError(Exception):
    """Levantada ao tentar submeter respostas a um simulado ja finalizado."""


class QuestoesInsuficientesError(Exception):
    """Levantada quando nao ha questoes suficientes para gerar o simulado."""


class SimuladoService:
    """Orquestra as regras de negocio dos simulados."""

    def __init__(
        self,
        simulado_repo: SimuladoRepository,
        questao_repo: QuestaoRepository,
    ):
        self.simulado_repo = simulado_repo
        self.questao_repo = questao_repo

    def criar(self, dados: SimuladoCreate) -> tuple[Simulado, list[int]]:
        """Cria um simulado e seleciona questoes aleatorias.

        No modo "sem_repetir", exclui questoes ja respondidas em qualquer
        simulado anterior, para cobrir o banco inteiro sem repeticao.
        """
        ciclo_atual = self.questao_repo.obter_ciclo_atual()

        excluir_ids = None
        if dados.modo == "sem_repetir":
            excluir_ids = self.questao_repo.ids_respondidas_no_ciclo(ciclo_atual)

        questoes = self.questao_repo.listar_aleatorio(
            quantidade=dados.quantidade,
            ano=dados.ano,
            tipo=dados.tipo,
            dificuldade=dados.dificuldade,
            excluir_ids=excluir_ids,
        )

        if len(questoes) < dados.quantidade:
            disponivel = len(questoes)
            if dados.modo == "sem_repetir":
                motivo = (
                    "ja foram todas respondidas no modo sem repetir "
                    "(reinicie a cobertura ou use o modo aleatorio)"
                )
            else:
                motivo = "disponiveis com os filtros informados"
            raise QuestoesInsuficientesError(
                f"Solicitadas {dados.quantidade} questoes, "
                f"mas apenas {disponivel} {motivo}."
            )

        questao_ids = [q.id for q in questoes]
        simulado = self.simulado_repo.criar(
            nome=dados.nome,
            total_questoes=len(questoes),
            questao_ids=questao_ids,
            ciclo=ciclo_atual,
        )

        return simulado, questao_ids

    def buscar(self, simulado_id: int) -> Simulado:
        simulado = self.simulado_repo.buscar_por_id(simulado_id)
        if simulado is None:
            raise SimuladoNaoEncontradoError(f"Simulado {simulado_id} nao encontrado.")
        return simulado

    def listar(self) -> list[Simulado]:
        return self.simulado_repo.listar()

    def submeter(self, simulado_id: int, dados: SimuladoSubmit) -> Simulado:
        """Recebe as respostas, corrige automaticamente e calcula a nota."""
        simulado = self.buscar(simulado_id)

        if simulado.finalizado:
            raise SimuladoJaFinalizadoError(
                f"Simulado {simulado_id} ja foi finalizado."
            )

        respostas_para_salvar = []
        for resp in dados.respostas:
            questao = self.questao_repo.buscar_por_id(resp.questao_id)
            if questao is None:
                continue

            correta = resp.alternativa_escolhida.upper() == questao.resposta.upper()
            respostas_para_salvar.append(
                {
                    "questao_id": resp.questao_id,
                    "alternativa_escolhida": resp.alternativa_escolhida.upper(),
                    "correta": correta,
                    "tempo_resposta": resp.tempo_resposta,
                }
            )

        self.simulado_repo.adicionar_respostas(simulado, respostas_para_salvar)
        return simulado

    def remover(self, simulado_id: int) -> None:
        self.simulado_repo.remover(self.buscar(simulado_id))

    def dashboard(self) -> dict:
        """Monta as estatisticas gerais de desempenho."""
        total = self.simulado_repo.contar()
        finalizados = self.simulado_repo.contar(finalizado=True)
        media = self.simulado_repo.media_nota()
        acertos, respondidas = self.simulado_repo.total_acertos_e_respostas()

        taxa = round((acertos / respondidas) * 100, 2) if respondidas > 0 else 0.0

        por_ano = self.simulado_repo.desempenho_por_ano()
        por_tipo = self.simulado_repo.desempenho_por_tipo()
        por_assunto = self.simulado_repo.desempenho_por_assunto()

        return {
            "total_simulados": total,
            "simulados_finalizados": finalizados,
            "media_nota": media,
            "total_questoes_respondidas": respondidas,
            "total_acertos": acertos,
            "taxa_acerto_geral": taxa,
            "desempenho_por_ano": por_ano,
            "desempenho_por_tipo": por_tipo,
            "desempenho_por_assunto": por_assunto,
        }

    def relatorio(self) -> dict:
        """Relatorio completo para revisao: desempenho geral, prioridades
        de estudo (assuntos mais fracos) e a lista de questoes erradas."""
        dados_dashboard = self.dashboard()

        prioridades = sorted(
            (
                item
                for item in dados_dashboard["desempenho_por_assunto"]
                if item["taxa"] < 70
            ),
            key=lambda item: item["taxa"],
        )[:5]

        return {
            **dados_dashboard,
            "prioridades_de_estudo": prioridades,
            "questoes_erradas": self.simulado_repo.questoes_erradas(),
        }
