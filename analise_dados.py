import pandas as pd

dados = pd.read_csv("data/energydata_complete.csv")
dados["date"]= pd.to_datetime(dados["date"])

print(dados.head())
print(dados.shape)

dados.info()

print("Primeira data: ", dados["date"].min())
print("Última data: ", dados["date"].max())
print("Datas em ordem: ", dados["date"].is_monotonic_increasing)
print("Horários repetidos: ", dados["date"].duplicated().sum())

intervalos = dados["date"].diff()
print(intervalos.value_counts())


consumo = dados[["Appliances"]]
resumo_consumo = consumo.describe()

print("Resumo do consumo dos aparelhos, em Wh: ")
print(resumo_consumo)

maiores_consumos = dados.nlargest(10, "Appliances")
colunas_consulta = ["date", "Appliances"]

print("Dez registros com maior consumo: ")
print(maiores_consumos[colunas_consulta])