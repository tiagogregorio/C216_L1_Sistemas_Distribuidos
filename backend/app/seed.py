"""Script de seed para popular o banco com questoes do ENADE."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL
from app.database.base import Base
from app.models.questao import Questao

QUESTOES_SEED = [
    # === ENADE 2019 - Componente Especifico ===
    {
        "ano": 2019,
        "numero": 9,
        "tipo": "CE",
        "enunciado": (
            "O MergeSort e um metodo de ordenacao que combina dois vetores "
            "ordenados e cria um terceiro vetor maior tambem ordenado. "
            "Considerando o codigo apresentado, a implementacao do prototipo "
            "do metodo sort da classe MergeSort e:"
        ),
        "alternativa_a": (
            "if (hi == lo) return; int mid = lo + (hi - lo)/2; "
            "sort(a, lo, mid); sort(a, mid, hi); merge(a, lo, mid, hi);"
        ),
        "alternativa_b": (
            "if (hi > lo) return; int mid = lo + (hi - lo)/2; "
            "sort(a, lo, mid); sort(a, mid, hi); merge(a, lo, mid, hi);"
        ),
        "alternativa_c": (
            "if (hi <= lo) return; int mid = lo + (hi - lo)/2; "
            "sort(a, lo, mid); sort(a, mid, hi); merge(a, lo, mid, hi);"
        ),
        "alternativa_d": (
            "if (hi > lo) return; int mid = lo + (hi - lo)/2; "
            "sort(a, lo, mid); sort(a, mid+1, hi); merge(a, lo, mid, hi);"
        ),
        "alternativa_e": (
            "if (hi <= lo) return; int mid = lo + (hi - lo)/2; "
            "sort(a, lo, mid); sort(a, mid+1, hi); merge(a, lo, mid, hi);"
        ),
        "resposta": "E",
        "assunto": "Algoritmos de Ordenacao",
        "dificuldade": "medio",
    },
    {
        "ano": 2019,
        "numero": 10,
        "tipo": "CE",
        "enunciado": (
            "Pesquisadores treinaram um sistema de Inteligencia Artificial "
            "com exames de retina de 284335 pacientes em busca de padroes "
            "nos cruzamentos de vasos sanguineos para identificar sinais "
            "indicadores de doencas cardiovasculares. Acerca do caso, avalie: "
            "I. O conjunto de dados utilizado corresponde aos exames de retina. "
            "II. A selecao de caracteristicas equivale ao cruzamento de vasos. "
            "III. A classificacao corresponde a identificar sinais de doencas."
        ),
        "alternativa_a": "I, apenas.",
        "alternativa_b": "II, apenas.",
        "alternativa_c": "I e III, apenas.",
        "alternativa_d": "II e III, apenas.",
        "alternativa_e": "I, II e III.",
        "resposta": "E",
        "assunto": "Inteligencia Artificial",
        "dificuldade": "facil",
    },
    {
        "ano": 2019,
        "numero": 11,
        "tipo": "CE",
        "enunciado": (
            "O gestor de um hotel precisa satisfazer a demanda de grupos "
            "de eventos pelo uso exclusivo de auditorios usando o menor "
            "numero possivel. A tabela apresenta os conflitos entre grupos. "
            "O numero minimo de auditorios que satisfaz todas as demandas e de:"
        ),
        "alternativa_a": "um.",
        "alternativa_b": "dois.",
        "alternativa_c": "tres.",
        "alternativa_d": "quatro.",
        "alternativa_e": "cinco.",
        "resposta": "C",
        "assunto": "Grafos",
        "dificuldade": "medio",
    },
    {
        "ano": 2019,
        "numero": 18,
        "tipo": "CE",
        "enunciado": (
            "O algoritmo DES cifra blocos de 64 bits usando chaves de 56 bits. "
            "O 3DES usa tres execucoes do DES com chaves de ate 168 bits. "
            "Para que o 3DES seja capaz de decifrar mensagens cifradas com "
            "o DES, sua implementacao deve ser:"
        ),
        "alternativa_a": "D(C(D(m, ka), kb), kc), sendo ka != kb != kc.",
        "alternativa_b": "D(D(D(m, ka), kb), kc), sendo ka != kb != kc.",
        "alternativa_c": "D(D(D(m, ka), kb), kc), sendo ka = kb = kc.",
        "alternativa_d": "D(C(D(m, ka), kb), kc), sendo ka = kb = kc.",
        "alternativa_e": "D(D(C(m, ka), kb), kc), sendo ka = kb = kc.",
        "resposta": "D",
        "assunto": "Criptografia",
        "dificuldade": "dificil",
    },
    {
        "ano": 2019,
        "numero": 20,
        "tipo": "CE",
        "enunciado": (
            "Rigidez e a tendencia de um software ser dificil de modificar. "
            "O trecho de codigo mostra um sistema com suporte a comunicacao "
            "entre modems. No projeto do codigo, um sintoma de rigidez e que:"
        ),
        "alternativa_a": (
            "Se o suporte ao modem Ernie for removido, sera necessario "
            "remover a estrutura Ernie."
        ),
        "alternativa_b": (
            "Se um novo modem for adicionado, sera necessario alterar "
            "o numero de parametros do LogOn."
        ),
        "alternativa_c": (
            "Se um novo modem for adicionado, e necessario copiar todo "
            "o codigo de outra estrutura."
        ),
        "alternativa_d": (
            "Se a politica do Hayes sofrer alteracao, pode ser necessario "
            "alterar OpenHayesChannel e a estrutura Hayes."
        ),
        "alternativa_e": (
            "Se a politica do Courrier sofrer alteracao, pode ser necessario "
            "alterar OpenCourrierChannel, LogOn e criar OpenErnieChannel."
        ),
        "resposta": "E",
        "assunto": "Engenharia de Software",
        "dificuldade": "dificil",
    },
    {
        "ano": 2019,
        "numero": 24,
        "tipo": "CE",
        "enunciado": (
            "Protocolos de roteamento de estado de enlace utilizam difusao "
            "para propagar informacoes. Uma spanning tree minima de um grafo "
            "com 6 roteadores (A-F) e os custos dados, o custo da spanning "
            "tree minima correspondente e exatamente:"
        ),
        "alternativa_a": "5.",
        "alternativa_b": "7.",
        "alternativa_c": "8.",
        "alternativa_d": "9.",
        "alternativa_e": "11.",
        "resposta": "C",
        "assunto": "Redes de Computadores",
        "dificuldade": "medio",
    },
    {
        "ano": 2019,
        "numero": 26,
        "tipo": "CE",
        "enunciado": (
            "O controlador PID e o algoritmo de controle mais utilizado "
            "na industria. Considerando o esquema de controle PID para "
            "temperatura de um forno, a linha 12 do codigo deve ser "
            "completada com:"
        ),
        "alternativa_a": "kp * Erro + ki * ITerm;",
        "alternativa_b": "ki/kp * ITerm + kd/kp * dErro;",
        "alternativa_c": "kp * Erro + kd * dErro * dErro;",
        "alternativa_d": "kp * Erro + ki * ITerm + kd * dErro;",
        "alternativa_e": "kp * Erro + ki * ITerm + kd * dErro * dErro;",
        "resposta": "D",
        "assunto": "Controle e Automacao",
        "dificuldade": "medio",
    },
    {
        "ano": 2019,
        "numero": 27,
        "tipo": "CE",
        "enunciado": (
            "Padroes de projeto sao solucoes gerais para problemas frequentes. "
            "O diagrama UML ilustra o padrao Strategy. Avalie: "
            "I. Strategy pode ser classe abstrata ou interface. "
            "II. Pode ser usado para metodos de ordenacao com diferentes "
            "criterios de comparacao. "
            "III. O baixo acoplamento permite incluir ou retirar estrategias "
            "sem alterar as demais classes. "
            "IV. O uso do padrao Singleton permitiria centralizar a logica "
            "de selecao da estrategia."
        ),
        "alternativa_a": "I e II.",
        "alternativa_b": "I e IV.",
        "alternativa_c": "III e IV.",
        "alternativa_d": "I, II e III.",
        "alternativa_e": "II, III e IV.",
        "resposta": "D",
        "assunto": "Padroes de Projeto",
        "dificuldade": "medio",
    },
    {
        "ano": 2019,
        "numero": 30,
        "tipo": "CE",
        "enunciado": (
            "Um Container de Servlets gerencia aplicacoes com conteudo "
            "dinamico. O Servlet ContaRequisicoes mantem um contador. "
            "I. O codigo apresenta uma condicao de corrida. "
            "II. Substituir a linha 5 por synchronized(this){...} garante "
            "o correto funcionamento. "
            "III. Obter a trava do objeto request garante o correto "
            "funcionamento."
        ),
        "alternativa_a": "I, apenas.",
        "alternativa_b": "II, apenas.",
        "alternativa_c": "I e III, apenas.",
        "alternativa_d": "II e III, apenas.",
        "alternativa_e": "I, II e III.",
        "resposta": "D",
        "assunto": "Programacao Concorrente",
        "dificuldade": "dificil",
    },
    {
        "ano": 2019,
        "numero": 34,
        "tipo": "CE",
        "enunciado": (
            "O algoritmo Round Robin atribui um quantum a cada processo. "
            "Um sistema precisa executar dois processos de 20 ms cada. "
            "Para minimizar o tempo de resposta, o Quantum e o tempo de "
            "troca de contexto devem ser, respectivamente:"
        ),
        "alternativa_a": "5 ms e 1 ms.",
        "alternativa_b": "4 ms e 2 ms.",
        "alternativa_c": "5 ms e 3 ms.",
        "alternativa_d": "2 ms e 1 ms.",
        "alternativa_e": "2 ms e 2 ms.",
        "resposta": "A",
        "assunto": "Sistemas Operacionais",
        "dificuldade": "medio",
    },
    # === ENADE 2014 - Componente Especifico ===
    {
        "ano": 2014,
        "numero": 15,
        "tipo": "CE",
        "enunciado": (
            "Observe o programa classificador (sort) em pseudocodigo. "
            "Esse programa classifica, em ordem:"
        ),
        "alternativa_a": (
            "decrescente, notas de alunos e nomes de alunos de mesma nota."
        ),
        "alternativa_b": (
            "alfabetica crescente, nomes e notas de alunos de mesmo nome."
        ),
        "alternativa_c": "decrescente, notas de alunos.",
        "alternativa_d": "alfabetica crescente, nomes de alunos.",
        "alternativa_e": "crescente, notas de alunos.",
        "resposta": "C",
        "assunto": "Algoritmos de Ordenacao",
        "dificuldade": "facil",
    },
    {
        "ano": 2014,
        "numero": 19,
        "tipo": "CE",
        "enunciado": (
            "O Marco Civil da Internet defende a neutralidade da rede, "
            "ou seja, nenhuma empresa podera criar barreiras para algum "
            "tipo de conteudo. Avalie: "
            "I. O roteamento interno deve tratar todos os protocolos "
            "de modo igualitario. "
            "II. A mudanca de cenario e exemplo de como as empresas devem "
            "estar continuamente se atualizando. "
            "III. A lei permite que um provedor aumente a prioridade de "
            "um trafego em relacao a outro."
        ),
        "alternativa_a": "II, apenas.",
        "alternativa_b": "III, apenas.",
        "alternativa_c": "I e II, apenas.",
        "alternativa_d": "I e III, apenas.",
        "alternativa_e": "I, II e III.",
        "resposta": "A",
        "assunto": "Redes de Computadores",
        "dificuldade": "facil",
    },
    {
        "ano": 2014,
        "numero": 22,
        "tipo": "CE",
        "enunciado": (
            "Dois problemas de pesquisa operacional: o problema do carteiro "
            "chines (PCC) e o problema do caixeiro viajante (PCV). "
            "Avalie: "
            "I. Se o grafo for euleriano, o PCV pode ser resolvido sem "
            "visitas repetidas. "
            "II. Se todas as cidades se conectam, a solucao do PCV e um "
            "ciclo hamiltoniano de menor deslocamento. "
            "III. Se o grafo for euleriano e possuir ciclo hamiltoniano, "
            "PCC e PCV dao a mesma trilha."
        ),
        "alternativa_a": "II, apenas.",
        "alternativa_b": "III, apenas.",
        "alternativa_c": "I e II, apenas.",
        "alternativa_d": "I e III, apenas.",
        "alternativa_e": "I, II e III.",
        "resposta": "A",
        "assunto": "Grafos",
        "dificuldade": "dificil",
    },
    {
        "ano": 2014,
        "numero": 24,
        "tipo": "CE",
        "enunciado": (
            "Acerca do protocolo TCP, considere a comunicacao entre A e B. "
            "A enviou 4 segmentos de 40 bytes (seq=20,60,100,140). "
            "O segundo segmento foi perdido. O numero de confirmacao (ACK) "
            "enviado de B para A no instante t0 e igual a:"
        ),
        "alternativa_a": "20.",
        "alternativa_b": "59.",
        "alternativa_c": "60.",
        "alternativa_d": "100.",
        "alternativa_e": "140.",
        "resposta": "C",
        "assunto": "Redes de Computadores",
        "dificuldade": "medio",
    },
    {
        "ano": 2014,
        "numero": 29,
        "tipo": "CE",
        "enunciado": (
            "Expressoes regulares descrevem linguagens regulares. "
            "Dadas R1=a*ba*ba*ba*, R2=a*(a|b)a(a|b)*, "
            "R3=a*ab*a(a|b), R4=(a|b)*, "
            "a cadeia 'abbb' esta contida apenas nas linguagens de:"
        ),
        "alternativa_a": "R1 e R4.",
        "alternativa_b": "R2 e R3.",
        "alternativa_c": "R2 e R4.",
        "alternativa_d": "R1 e R3.",
        "alternativa_e": "R2, R3 e R4.",
        "resposta": "A",
        "assunto": "Linguagens Formais",
        "dificuldade": "dificil",
    },
]


def executar_seed():
    """Popula o banco de dados com as questoes do ENADE."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    existentes = session.query(Questao).count()
    if existentes > 0:
        print(f"Banco ja possui {existentes} questoes. Seed ignorado.")
        session.close()
        return

    for dados in QUESTOES_SEED:
        questao = Questao(**dados)
        session.add(questao)

    session.commit()
    total = len(QUESTOES_SEED)
    print(f"Seed concluido: {total} questoes do ENADE inseridas.")
    session.close()


if __name__ == "__main__":
    executar_seed()
