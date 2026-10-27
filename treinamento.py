from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from preparacao_dados import preparar_dados, COLUNA_ALVO


def avaliar_previsoes(valores_reais, previsoes):
    mae = mean_absolute_error(valores_reais, previsoes)
    mse = mean_squared_error(valores_reais, previsoes)
    r2 = r2_score(valores_reais, previsoes)

    return mae, mse, r2


if __name__ == "__main__":
    treino, validacao, teste = preparar_dados(
        "data/energydata_complete.csv"
    )

    valores_reais = validacao[COLUNA_ALVO]
    previsoes_referencia = validacao["Appliances"]

    mae, mse, r2 = avaliar_previsoes(
        valores_reais,
        previsoes_referencia,
    )

    print("\n=== REFERÊNCIA: REPETIR O ÚLTIMO CONSUMO ===\n")
    print("Conjunto avaliado: validação")
    print("Quantidade de exemplos:", len(validacao))

    print("\n=== MÉTRICAS ===\n")
    print(f"MAE: {mae:.2f} Wh")
    print(f"MSE: {mse:.2f} Wh²")
    print(f"R²: {r2:.4f}")