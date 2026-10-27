import pandas as pd

dados = pd.read_csv("data/energydata_complete.csv")
dados["date"] = pd.to_datetime(dados["date"])

dados["consumo_futuro"] = dados["Appliances"].shift(-1)

quantidade_antes = len(dados)
dados  = dados.dropna(subset=["consumo_futuro"]).copy()

quantidade_depois = len(dados)
quantidade_removida = quantidade_antes - quantidade_depois

print("Registros antes da remoção de valores nulos:", quantidade_antes)
print("Registros depois da remoção de valores nulos:", quantidade_depois)
print("Registros removidos:", quantidade_removida)

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

print("Primeiros registros:")
print(conferencia.head())

print("Últimos registros:")
print(conferencia.tail())

colunas_entrada = ["Appliances", "hora", "dia_da_semana"]

x = dados[colunas_entrada]
y = dados["consumo_futuro"]

print("Colunas de entrada: ")
print(x.columns.tolist())

print("Quantidade de linhas e colunas de X:", x.shape)
print("Quantidade de respostas em y:", len(y))
