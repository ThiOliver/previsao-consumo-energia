import pandas as pd


COLUNAS_ENTRADA = ["Appliances", "hora", "dia_da_semana"]
COLUNA_ALVO = "consumo_futuro"


def preparar_dados(caminho_csv):
    dados = pd.read_csv(caminho_csv)
    dados["date"] = pd.to_datetime(dados["date"])

    dados[COLUNA_ALVO] = dados["Appliances"].shift(-1)
    dados = dados.dropna(subset=[COLUNA_ALVO]).copy()

    dados["hora"] = dados["date"].dt.hour
    dados["dia_da_semana"] = dados["date"].dt.dayofweek

    quantidade_total = len(dados)

    inicio_validacao = int(quantidade_total * 0.70)
    inicio_teste = int(quantidade_total * 0.85)

    treino = dados.iloc[:inicio_validacao - 1].copy()
    validacao = dados.iloc[inicio_validacao:inicio_teste - 1].copy()
    teste = dados.iloc[inicio_teste:].copy()

    return treino, validacao, teste


if __name__ == "__main__":
    treino, validacao, teste = preparar_dados(
        "data/energydata_complete.csv"
    )

    print("\n=== ENTRADAS E ALVO ===\n")
    print("Entradas:", COLUNAS_ENTRADA)
    print("Alvo:", COLUNA_ALVO)

    print("\n=== QUANTIDADE DE EXEMPLOS ===\n")
    print("Treino:", len(treino))
    print("Validação:", len(validacao))
    print("Teste:", len(teste))

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

    print("\n=== AMOSTRA DO TREINO ===\n")
    colunas_consulta = ["date"] + COLUNAS_ENTRADA + [COLUNA_ALVO]
    print(treino[colunas_consulta].head())