# Prepara exemplos para prever o consumo do próximo intervalo de dez minutos.
import pandas as pd


# Centraliza os nomes das entradas e da resposta para reutilização no treinamento.
COLUNAS_ENTRADA = ["Appliances", "hora", "dia_da_semana"]
COLUNA_ALVO = "consumo_futuro"


# Recebe o caminho do CSV e devolve três tabelas: treino, validação e teste.
# Pressupõe os horários já verificados: ordenados, únicos e separados por dez minutos.
def preparar_dados(caminho_csv):
    # Lê uma tabela nova em memória; o CSV original não é modificado.
    dados = pd.read_csv(caminho_csv)
    dados["date"] = pd.to_datetime(dados["date"])

    # A próxima medição é a resposta esperada, nunca uma entrada do modelo.
    # Remove o último registro, cujo consumo futuro não está disponível na base.
    dados[COLUNA_ALVO] = dados["Appliances"].shift(-1)
    dados = dados.dropna(subset=[COLUNA_ALVO]).copy()

    # Extrai o calendário conhecido: hora 0–23 e dia 0–6 (segunda a domingo).
    dados["hora"] = dados["date"].dt.hour
    dados["dia_da_semana"] = dados["date"].dt.dayofweek

    # Calcula limites aproximados de 70% para treino, 15% para validação e 15% para teste.
    quantidade_total = len(dados)

    inicio_validacao = int(quantidade_total * 0.70)
    inicio_teste = int(quantidade_total * 0.85)

    # Mantém a ordem temporal e exclui um exemplo em cada fronteira.
    # Assim, o alvo anterior não alcança o período de entradas da parte seguinte.
    treino = dados.iloc[:inicio_validacao - 1].copy()
    validacao = dados.iloc[inicio_validacao:inicio_teste - 1].copy()
    teste = dados.iloc[inicio_teste:].copy()

    # Entrega os resultados a quem chamou a função, sem imprimi-los automaticamente.
    return treino, validacao, teste


# Executa a conferência somente ao rodar este arquivo diretamente.
# Importar a função no treinamento não dispara estas impressões.
if __name__ == "__main__":
    treino, validacao, teste = preparar_dados(
        "data/energydata_complete.csv"
    )

    # Mostra as colunas escolhidas e os tamanhos das partes.
    print("\n=== ENTRADAS E ALVO ===\n")
    print("Entradas:", COLUNAS_ENTRADA)
    print("Alvo:", COLUNA_ALVO)

    print("\n=== QUANTIDADE DE EXEMPLOS ===\n")
    print("Treino:", len(treino))
    print("Validação:", len(validacao))
    print("Teste:", len(teste))

    # Os horários abaixo são das entradas; cada alvo corresponde a dez minutos depois.
    print("\n=== PERÍODOS DAS ENTRADAS ===\n")

    print("TREINO")
    print("Início:", treino["date"].min())
    print("Fim:", treino["date"].max())

    print("\nVALIDAÇÃO")
    print("Início:", validacao["date"].min())
    print("Fim:", validacao["date"].max())

    print("\nTESTE")
    print("Início:", teste["date"].min())
    print("Fim:", teste["date"].max())

    # Exibe entradas e alvo lado a lado para conferir o alinhamento.
    print("\n=== AMOSTRA DO TREINO ===\n")
    colunas_consulta = ["date"] + COLUNAS_ENTRADA + [COLUNA_ALVO]
    print(treino[colunas_consulta].head())
