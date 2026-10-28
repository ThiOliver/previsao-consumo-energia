# Explora a base sem alterar o CSV original.
# Pandas trabalha com tabelas; pyplot cria gráficos.
import pandas as pd
import matplotlib.pyplot as plt

# Carrega a tabela em memória e interpreta os horários como datas.
dados = pd.read_csv("data/energydata_complete.csv")
dados["date"]= pd.to_datetime(dados["date"])

# Mostra amostra, dimensões, tipos e quantidade de valores preenchidos.
print(dados.head())
print(dados.shape)

dados.info()

# Confere período, ordem temporal e horários repetidos antes de preparar previsões.
print("Primeira data: ", dados["date"].min())
print("Última data: ", dados["date"].max())
print("Datas em ordem: ", dados["date"].is_monotonic_increasing)
print("Horários repetidos: ", dados["date"].duplicated().sum())

# Conta as diferenças entre horários consecutivos.
# O primeiro registro não tem anterior e fica fora dessa contagem.
intervalos = dados["date"].diff()
print(intervalos.value_counts())


# Resume o consumo em Wh: média, dispersão, quartis e valores extremos.
consumo = dados[["Appliances"]]
resumo_consumo = consumo.describe()

print("Resumo do consumo dos aparelhos, em Wh: ")
print(resumo_consumo)

# Consulta os maiores consumos sem removê-los: um pico não é necessariamente um erro.
maiores_consumos = dados.nlargest(10, "Appliances")
colunas_consulta = ["date", "Appliances"]

print("Dez registros com maior consumo: ")
print(maiores_consumos[colunas_consulta])

# Agrupa o consumo em 30 faixas; a altura das barras representa a contagem de registros.
plt.figure(figsize=(8, 5))
plt.hist(dados["Appliances"], bins=30, edgecolor="black")
plt.title("Distribuição do consumo dos aparelhos")
plt.xlabel("Energia por intervalo de 10 minutos (Wh)")
plt.ylabel("Quantidade de registros")

# Ajusta o espaço dos títulos, salva a imagem na pasta de execução e libera a figura.
plt.tight_layout()
plt.savefig("distribuicao_consumo.png")
plt.close()

print("Gráfico salvo em distribuicao_consumo.png")
