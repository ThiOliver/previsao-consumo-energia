import pandas as pd
import matplotlib.pyplot as plt

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

plt.figure(figsize=(8, 5))
plt.hist(dados["Appliances"], bins=30, edgecolor="black")
plt.title("Distribuição do consumo dos aparelhos")
plt.xlabel("Energia por intervalo de 10 minutos (Wh)")
plt.ylabel("Quantidade de registros")

plt.tight_layout()
plt.savefig("distribuicao_consumo.png")
plt.close()

print("Gráfico salvo em distribuicao_consumo.png")
