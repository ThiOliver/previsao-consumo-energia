# Compara uma previsão simples com a regressão linear usando a validação.
# As importações fornecem métricas, tratamentos e componentes do pipeline.
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor

# Path organiza caminhos e permite criar a pasta do modelo.
from pathlib import Path

# Joblib salva e recupera o pipeline treinado.
import joblib

# Reutiliza a preparação e os mesmos nomes de entradas e alvo.
from preparacao_dados import preparar_dados, COLUNA_ALVO, COLUNAS_ENTRADA


# Recebe respostas reais e previsões alinhadas e devolve MAE (Wh), MSE (Wh²) e R².
# MAE mede o erro absoluto médio; MSE dá mais peso aos erros grandes.
# R² compara com a média real do conjunto avaliado e não representa acurácia.
def avaliar_previsoes(valores_reais, previsoes):
    mae = mean_absolute_error(valores_reais, previsoes)
    mse = mean_squared_error(valores_reais, previsoes)
    r2 = r2_score(valores_reais, previsoes)

    return mae, mse, r2

# Monta o pipeline ainda não treinado. Os tratamentos aprendem seus valores no fit.
def criar_modelo():
    # Preenche ausências com a mediana e ajusta a escala usando apenas o treino.
    tratamento_consumo = Pipeline([
        ("preencher", SimpleImputer(strategy="median")),
        ("padronizar", StandardScaler()),
    ])

    # Converte hora e dia em indicadores 0/1, sem impor uma ordem numérica às categorias.
    # Uma categoria desconhecida não interrompe a transformação.
    tratamento_calendario = Pipeline([
        ("preencher", SimpleImputer(strategy="most_frequent")),
        ("codificar", OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False,
        )),
    ])

    # Direciona cada coluna ao tratamento apropriado.
    tratamentos = ColumnTransformer([
        ("consumo", tratamento_consumo, ["Appliances"]),
        ("calendario", tratamento_calendario, ["hora", "dia_da_semana"]),
    ])

    # Une tratamentos e regressão para aplicar a mesma sequência nas previsões.
    modelo = Pipeline([
        ("tratamentos", tratamentos),
        ("regressao", LinearRegression()),
    ])

    return modelo

# Executa o experimento somente ao rodar este arquivo, não ao importá-lo.
if __name__ == "__main__":
    # Separa os períodos: validação para comparar e teste para avaliação final.
    treino, validacao, teste = preparar_dados(
        "data/energydata_complete.csv"
    )

    # Separa entradas e respostas para não fornecer o consumo futuro como entrada.
    x_treino = treino[COLUNAS_ENTRADA]
    y_treino = treino[COLUNA_ALVO]

    x_validacao = validacao[COLUNAS_ENTRADA]
    y_validacao = validacao[COLUNA_ALVO]

    # Referência: repetir o último consumo conhecido.
    previsoes_referencia = validacao["Appliances"]

    mae_referencia, mse_referencia, r2_referencia = avaliar_previsoes(
        y_validacao,
        previsoes_referencia,
    )

    # Mostra a referência; as casas decimais afetam apenas a apresentação dos números.
    print("\n=== REFERÊNCIA: REPETIR O ÚLTIMO CONSUMO ===\n")
    print("Conjunto avaliado: validação")
    print("Quantidade de exemplos:", len(validacao))
    print(f"MAE: {mae_referencia:.2f} Wh")
    print(f"MSE: {mse_referencia:.2f} Wh²")
    print(f"R²: {r2_referencia:.4f}")

    # Modelo: aprender com o treino e prever na validação.
    modelo = criar_modelo()
    modelo.fit(x_treino, y_treino)

    # Reutiliza na validação os tratamentos ajustados no treino, sem novo fit.
    previsoes_modelo = modelo.predict(x_validacao)

    mae_modelo, mse_modelo, r2_modelo = avaliar_previsoes(
        y_validacao,
        previsoes_modelo,
    )

    # Apresenta as métricas do modelo separadas das métricas da referência.
    print("\n=== REGRESSÃO LINEAR — VALIDAÇÃO ===\n")
    print(f"MAE: {mae_modelo:.2f} Wh")
    print(f"MSE: {mse_modelo:.2f} Wh²")
    print(f"R²: {r2_modelo:.4f}")


    # Define uma floresta de tamanho limitado para comparação.
    # A semente fixa permite repetir o experimento com a mesma configuração.
    floresta = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=1,
    )

    # Cria um pipeline independente, mantendo os mesmos tratamentos das entradas.
    # Substitui apenas o estimador da etapa chamada "regressao".
    modelo_floresta = criar_modelo()
    modelo_floresta.set_params(regressao=floresta)

    # Aprende somente com o treino e calcula previsões na validação.
    modelo_floresta.fit(x_treino, y_treino)
    previsoes_floresta = modelo_floresta.predict(x_validacao)

    # Usa as mesmas métricas e respostas reais para comparar os métodos.
    mae_floresta, mse_floresta, r2_floresta = avaliar_previsoes(
        y_validacao,
        previsoes_floresta,
    )

    print("\n=== FLORESTA ALEATÓRIA — VALIDAÇÃO ===\n")
    print(f"MAE: {mae_floresta:.2f} Wh")
    print(f"MSE: {mse_floresta:.2f} Wh²")
    print(f"R²: {r2_floresta:.4f}")


        # Escolha feita a partir da validação: regressão linear.
    # Mantém o modelo já ajustado somente no treino.
    modelo_escolhido = modelo

    # Separa as entradas e respostas do período final reservado.
    x_teste = teste[COLUNAS_ENTRADA]
    y_teste = teste[COLUNA_ALVO]

    # Avalia a referência no mesmo período para uma comparação justa.
    previsoes_referencia_teste = teste["Appliances"]

    mae_ref_teste, mse_ref_teste, r2_ref_teste = avaliar_previsoes(
        y_teste,
        previsoes_referencia_teste,
    )

    # Faz previsões no teste sem executar fit novamente.
    previsoes_teste = modelo_escolhido.predict(x_teste)

    mae_teste, mse_teste, r2_teste = avaliar_previsoes(
        y_teste,
        previsoes_teste,
    )

    print("\n=== REFERÊNCIA — TESTE ===\n")
    print("Quantidade de exemplos:", len(teste))
    print(f"MAE: {mae_ref_teste:.2f} Wh")
    print(f"MSE: {mse_ref_teste:.2f} Wh²")
    print(f"R²: {r2_ref_teste:.4f}")

    print("\n=== REGRESSÃO LINEAR — TESTE ===\n")
    print(f"MAE: {mae_teste:.2f} Wh")
    print(f"MSE: {mse_teste:.2f} Wh²")
    print(f"R²: {r2_teste:.4f}")


    # Cria a pasta de artefatos, caso ainda não exista.
    pasta_modelos = Path("models")
    pasta_modelos.mkdir(exist_ok=True)

    # Salva exatamente o pipeline avaliado, sem realizar novo treinamento.
    caminho_modelo = pasta_modelos / "pipeline_consumo.joblib"
    joblib.dump(modelo_escolhido, caminho_modelo)

    # Recupera o arquivo e confere uma previsão contra o modelo em memória.
    modelo_carregado = joblib.load(caminho_modelo)
    exemplo = x_validacao.head(1)

    previsao_original = modelo_escolhido.predict(exemplo)
    previsao_carregada = modelo_carregado.predict(exemplo)

    print("\n=== MODELO SALVO E RECUPERADO ===\n")
    print("Arquivo:", caminho_modelo)
    print(f"Previsão original: {previsao_original[0]:.2f} Wh")
    print(f"Previsão recuperada: {previsao_carregada[0]:.2f} Wh")

    # Interrompe a execução se a previsão mudar após salvar e carregar.
    assert abs(previsao_original[0] - previsao_carregada[0]) < 0.000001

    print("Verificação: previsões equivalentes.")


        # Reúne as métricas calculadas, sem arredondar os valores armazenados.
    resultados = [
        ["validacao", "referencia", mae_referencia, mse_referencia, r2_referencia],
        ["validacao", "regressao_linear", mae_modelo, mse_modelo, r2_modelo],
        ["validacao", "floresta_aleatoria", mae_floresta, mse_floresta, r2_floresta],
        ["teste", "referencia", mae_ref_teste, mse_ref_teste, r2_ref_teste],
        ["teste", "regressao_linear", mae_teste, mse_teste, r2_teste],
    ]

    # Define os nomes das colunas e as unidades das métricas.
    colunas_relatorio = ["conjunto", "metodo", "mae_wh", "mse_wh2", "r2"]
    tabela_metricas = pd.DataFrame(resultados, columns=colunas_relatorio)

    # Cria uma pasta própria para os resultados documentados.
    pasta_relatorios = Path("relatorios")
    pasta_relatorios.mkdir(exist_ok=True)

    # Salva a tabela sem acrescentar a numeração das linhas como coluna.
    caminho_metricas = pasta_relatorios / "metricas.csv"
    tabela_metricas.to_csv(caminho_metricas, index=False)

    # Arredonda apenas a tabela exibida; o CSV mantém a precisão dos resultados.
    print("\n=== RESUMO DOS EXPERIMENTOS ===\n")
    print(tabela_metricas.round(4).to_string(index=False))
    print("\nRelatório salvo em:", caminho_metricas)
