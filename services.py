# Path constrói caminhos; joblib recupera o pipeline salvo.
from pathlib import Path
import joblib
# Verifica se o resultado numérico é finito.
from math import isfinite
# Organiza as entradas no formato de tabela esperado pelo pipeline.
import pandas as pd


# Localiza o modelo a partir da pasta deste arquivo Python.
# Assim, não depende da pasta em que o terminal foi aberto.
PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_MODELO = PASTA_PROJETO / "models" / "pipeline_consumo.joblib"


# Recupera o pipeline treinado para uso pela aplicação.
def carregar_modelo():
    # Interrompe a inicialização com uma mensagem clara se faltar o artefato.
    if not CAMINHO_MODELO.is_file():
        raise FileNotFoundError(
            f"Arquivo do modelo não encontrado: {CAMINHO_MODELO}"
        )

    return joblib.load(CAMINHO_MODELO)

# Recebe o pipeline já carregado e um dicionário com as entradas validadas.
def prever_consumo(modelo, dados_entrada):
    if modelo is None:
        raise RuntimeError("O modelo não está disponível.")

    # Mantém os mesmos nomes e a mesma ordem das entradas do treinamento.
    colunas = ["Appliances", "hora", "dia_da_semana"]
    tabela = pd.DataFrame([dados_entrada], columns=colunas)

    # Executa os tratamentos e a regressão já treinados.
    resultado = float(modelo.predict(tabela)[0])

    # Um resultado não finito indica falha no processamento.
    if not isfinite(resultado):
        raise RuntimeError("O modelo retornou um resultado não finito.")

    # A regressão linear pode produzir valores negativos.
    # Não altera silenciosamente a previsão: rejeita uma estimativa fisicamente inválida.
    if resultado < 0:
        raise ValueError(
            "O modelo não produziu uma estimativa não negativa para estas entradas."
        )

    return resultado