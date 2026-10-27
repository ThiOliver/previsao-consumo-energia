import pandas as pd

dados = pd.read_csv("data/energydata_complete.csv")
dados["date"] = pd.to_datetime(dados["date"])

dados["consumo_futuro"] = dados["Appliances"].shift(-1)

quantidade_antes = len(dados)
dados  = dados.dropna(subset=["consumo_futuro"]).copy()

quantidade_depois = len(dados)
quantidade_removida = quantidade_antes - quantidade_depois

print("\n=== PREPARAÇÃO DO ALVO ===\n")

print("Registros antes:", quantidade_antes)
print("Registros depois:", quantidade_depois)
print("Registros removidos por falta de alvo:", quantidade_removida)

dados["hora"] = dados["date"].dt.hour
dados["dia_da_semana"] = dados["date"].dt.dayofweek


colunas_consulta = [
    "date", 
    "Appliances", 
    "hora",
    "dia_da_semana",
    "consumo_futuro"
]

conferencia = dados[colunas_consulta]

print("\n=== PRIMEIROS REGISTROS ===\n")
print(conferencia.head())

print("\n=== ÚLTIMOS REGISTROS ===\n")
print(conferencia.tail())

colunas_entrada = ["Appliances", "hora", "dia_da_semana"]

x = dados[colunas_entrada]
y = dados["consumo_futuro"]

print("\n=== COLUNAS DE ENTRADA ===\n")
print("Colunas de entrada: ")
print(x.columns.tolist())

print("\n=== FORMA DOS DADOS ===\n")
print("Quantidade de linhas e colunas de X:", x.shape)
print("Quantidade de respostas em y:", len(y))


quantidade_total = len(dados)

inicio_validacao = int(quantidade_total * 0.70)
inicio_teste = int(quantidade_total *0.85)

treino = dados.iloc[:inicio_validacao - 1].copy()
validacao = dados.iloc[inicio_validacao:inicio_teste - 1].copy()
teste = dados.iloc[inicio_teste:].copy()

x_treino = treino[colunas_entrada]
y_treino = treino["consumo_futuro"]

x_validacao = validacao[colunas_entrada]
y_validacao = validacao["consumo_futuro"]

x_teste = teste[colunas_entrada]
y_teste = teste["consumo_futuro"]

print("\n=== QUANTIDADE DE EXEMPLOS ===\n")

print("Treino:", len(x_treino))
print("Validação:", len(x_validacao))
print("Teste:", len(x_teste))

quantidade_utilizada = len(treino) + len(validacao) + len(teste)

print()
print("Excluídos nas fronteiras:", quantidade_total - quantidade_utilizada)

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