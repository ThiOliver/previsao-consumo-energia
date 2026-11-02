# Interface local: envia os dados ao FastAPI, sem carregar ou treinar o modelo.
from pathlib import Path
from math import isfinite

import pandas as pd
import requests
import streamlit as st


URL_API = "http://127.0.0.1:8000"
PASTA_PROJETO = Path(__file__).resolve().parent
DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
    "Sexta-feira", "Sábado", "Domingo",
]

# Configura a largura e o título da aba do navegador.
st.set_page_config(page_title="Energia | Previsão de consumo", page_icon="⚡", layout="wide")

# CSS altera apenas a aparência. As classes próprias estilizam os blocos HTML fixos.
st.markdown("""
<style>
.stApp { background: #0b1220; color: #e6edf7; }
.block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #f1f5ff; }
[data-testid="stSidebar"] { background: #101b2d; }
[data-testid="stForm"], .st-key-resultado {
    background: #142033; border: 1px solid #2b3c53; border-radius: 18px;
}
[data-testid="stMetric"] {
    background: #142033; border: 1px solid #2b3c53; border-radius: 14px; padding: 16px;
}
[data-testid="stMetricValue"] { color: #5eead4; }
[data-testid="stFormSubmitButton"] button {
    background: #2dd4bf; color: #082024; border: 0; border-radius: 10px;
    min-height: 48px; font-weight: 700;
}
[data-testid="stFormSubmitButton"] button:hover { background: #5eead4; color: #082024; }
.hero { background: linear-gradient(120deg, #152b43, #123438);
    border: 1px solid #2b4b5d; border-radius: 22px; padding: 28px 32px;
    margin: 12px 0 24px; color: #e9f4f5; }
.hero h1 { color: #f1f5ff; font-size: clamp(28px, 4vw, 42px); margin: 8px 0 12px; }
.hero p { color: #bed1de; max-width: 760px; font-size: 17px; line-height: 1.6; }
.eyebrow { font-size: 12px; font-weight: 700; letter-spacing: 2px; color: #5eead4; }
.chip { display: inline-block; padding: 6px 12px; margin: 8px 8px 0 0;
    border: 1px solid #41616f; border-radius: 30px; font-size: 12px; color: #daeaf2; }
.empty { text-align: center; padding: 32px 18px 20px; }
.empty .symbol { font-size: 44px; color: #5eead4; }
.empty p { color: #a9bbcf; }
.footer { border-top: 1px solid #2b3c53; margin-top: 26px; padding-top: 16px;
    font-size: 12px; color: #a9bbcf; }
</style>
""", unsafe_allow_html=True)

# A consulta de saúde verifica a API real; não simula disponibilidade.
with st.sidebar:
    st.markdown("## ⚡ Energia")
    st.caption("LABORATÓRIO DE PREVISÃO")
    st.divider()
    st.markdown("**Conexão com o serviço**")
    try:
        saude = requests.get(f"{URL_API}/health", timeout=3)
        saude.raise_for_status()
        estado = saude.json()
        if estado.get("status") == "ativo" and estado.get("modelo_carregado") is True:
            st.success("API conectada · modelo carregado")
        else:
            st.warning("Serviço sem confirmação de prontidão")
    except (requests.exceptions.RequestException, ValueError, AttributeError):
        st.warning("API indisponível no momento")
    st.button("Atualizar conexão", key="atualizar_conexao")
    st.divider()
    st.markdown("**Como experimentar**")
    st.write("1. Informe a última medição.\n2. Escolha o horário e o dia.\n3. Calcule a estimativa seguinte.")
    st.caption("Wh mede energia consumida. Não confunda com W, que mede potência.")
    st.divider()
    st.caption("Projeto acadêmico SCTEC\n\nDados: UCI · Appliances Energy Prediction")

# Cabeçalho editorial: apresenta objetivo e escopo sem prometer precisão individual.
st.markdown("""
<div class="hero">
    <div class="eyebrow">DADOS & INTELIGÊNCIA ARTIFICIAL</div>
    <h1>Consumo de energia, em perspectiva.</h1>
    <p>Transforme a última medição de energia em uma estimativa para os próximos
    dez minutos. Explore como o consumo e a rotina entram na previsão.</p>
    <span class="chip">Horizonte de 10 minutos</span>
    <span class="chip">Regressão linear</span>
    <span class="chip">Previsão em Wh</span>
</div>
""", unsafe_allow_html=True)

# A última resposta fica na sessão para não desaparecer ao navegar pela página.
if "ultima_previsao" not in st.session_state:
    st.session_state.ultima_previsao = None

simulador, historico, desempenho, sobre = st.tabs(["Simular consumo", "Explorar os dados", "Desempenho do modelo", "Sobre o projeto"])

with simulador:
    esquerda, direita = st.columns([1, 1.2], gap="large")
    with esquerda:
        with st.form("formulario_previsao"):
            st.subheader("01 · Sua última medição")
            st.caption("Use o calendário do registro conhecido, não o do intervalo futuro.")
            consumo = st.number_input(
                "Consumo do intervalo concluído (Wh)", min_value=0.0,
                value=60.0, step=10.0,
                help="Energia dos aparelhos nos últimos dez minutos completos.",
            )
            hora = st.number_input("Hora do registro", min_value=0, max_value=23, value=17, step=1)
            dia = st.selectbox("Dia da semana", DIAS_SEMANA)
            enviar = st.form_submit_button("Calcular próxima previsão →", type="primary", width="stretch")

        # O formulário faz a chamada somente quando o usuário confirma o envio.
        if enviar:
            st.session_state.ultima_previsao = None
            entrada = {"Appliances": float(consumo), "hora": int(hora), "dia_da_semana": DIAS_SEMANA.index(dia)}
            try:
                with st.spinner("Consultando o modelo na API..."):
                    resposta = requests.post(f"{URL_API}/predict", json=entrada, timeout=10)
                if resposta.status_code == 200:
                    resultado = resposta.json()
                    # Confere os campos necessários antes de guardar a resposta.
                    valor = float(resultado["previsao_wh"])
                    if not isfinite(valor) or valor < 0:
                        raise ValueError("Previsão inválida")
                    if resultado["unidade"] != "Wh" or resultado["horizonte_minutos"] != 10:
                        raise ValueError("Contrato de resposta inesperado")
                    st.session_state.ultima_previsao = {"entrada": entrada, "resposta": resultado, "valor": valor}
                else:
                    st.error(f"Previsão não concluída · HTTP {resposta.status_code}")
                    st.write(resposta.json().get("detail", "Resposta sem detalhes."))
            except requests.exceptions.Timeout:
                st.error("O serviço demorou mais de dez segundos para responder. Tente novamente.")
            except requests.exceptions.ConnectionError:
                st.error("Não foi possível conectar à API. Inicie o servidor FastAPI e tente novamente.")
            except requests.exceptions.RequestException:
                st.error("Falha na comunicação com a API. Tente novamente.")
            except (ValueError, KeyError, TypeError, AttributeError):
                st.error("O serviço retornou uma resposta em formato inesperado.")

    with direita:
        with st.container(border=True, key="resultado"):
            st.subheader("02 · Próximos dez minutos")
            ultima = st.session_state.ultima_previsao
            if ultima is None:
                st.markdown("""
                <div class="empty"><div class="symbol">↗</div>
                <h3>Uma medição. Uma nova perspectiva.</h3>
                <p>Preencha os campos ao lado e calcule sua primeira estimativa.</p></div>
                """, unsafe_allow_html=True)
                st.caption("Sugestão inicial: 60 Wh · 17h · segunda-feira.")
            else:
                # Usa a entrada efetivamente enviada, mesmo que o formulário seja editado depois.
                entrada_usada = ultima["entrada"]
                valor = ultima["valor"]
                conhecido = entrada_usada["Appliances"]
                diferenca = valor - conhecido
                st.metric("Energia estimada", f"{valor:.2f} Wh", delta=f"{diferenca:+.2f} Wh em relação ao último intervalo", delta_color="off")
                st.caption(f"Última simulação: {conhecido:g} Wh · {entrada_usada['hora']:02d}h · {DIAS_SEMANA[entrada_usada['dia_da_semana']]}. Recalcule após mudar as entradas.")
                # Compara dois valores distintos, sem inventar uma série histórica.
                comparacao = pd.DataFrame({"Intervalo": ["Último conhecido", "Próximo estimado"], "Energia (Wh)": [conhecido, valor]})
                st.bar_chart(comparacao, x="Intervalo", y="Energia (Wh)", color="#2dd4bf", height=220, sort=False)
                st.caption("Comparação com o último consumo, não com uma medição futura real. A diferença não representa erro de previsão.")
                # Extrapolação aritmética opcional: 6 intervalos por hora, 24 horas por dia.
                # A tarifa é informada pelo usuário; o modelo continua prevendo só dez minutos.
                with st.expander("Simular custo mensal"):
                    st.write("Quanto custaria manter este consumo de dez minutos durante o mês inteiro?")
                    tarifa = st.number_input("Tarifa informada (R$/kWh)", min_value=0.0, value=0.0, step=0.05, format="%.2f")
                    dias_mes = st.number_input("Dias do mês", min_value=28, max_value=31, value=30, step=1)
                    energia_mensal = valor / 1000 * 6 * 24 * dias_mes
                    st.metric("Energia mensal simulada", f"{energia_mensal:.2f} kWh")
                    if tarifa > 0:
                        custo_mensal = energia_mensal * tarifa
                        st.metric("Custo mensal simulado", f"R$ {custo_mensal:.2f}")
                    else:
                        st.info("Informe sua tarifa por kWh para calcular o custo.")
                    st.caption("Fórmula: (Wh previstos ÷ 1.000) × 6 × 24 × dias × tarifa. Supõe consumo constante, inclusive à noite. Não é uma previsão mensal nem a conta completa: não acrescenta tributos, bandeiras ou cobranças fixas à tarifa informada. Considera apenas o consumo dos aparelhos representado pelo modelo.")
                with st.expander("Detalhes da requisição e da resposta"):
                    st.write("Dados enviados ao FastAPI")
                    st.json(entrada_usada)
                    st.write("Resposta recebida")
                    st.json(ultima["resposta"])
        st.caption("Estimativa acadêmica para os aparelhos da residência estudada; não representa a conta de luz nem uma garantia de consumo.")

# Mantém a leitura histórica em cache; os dados servem somente às visualizações.
# A previsão da interface continua sendo calculada exclusivamente pelo FastAPI.
@st.cache_data
def carregar_historico(caminho_csv):
    tabela = pd.read_csv(caminho_csv, usecols=["date", "Appliances"])
    tabela["date"] = pd.to_datetime(tabela["date"])
    tabela["Consumo seguinte (Wh)"] = tabela["Appliances"].shift(-1)
    return tabela


with historico:
    st.subheader("O consumo por trás dos números")
    st.caption("Medições históricas da residência estudada · janeiro a maio de 2016. Não são dados ao vivo nem previsões do modelo.")
    caminho_dados = PASTA_PROJETO / "data" / "energydata_complete.csv"
    if not caminho_dados.is_file():
        st.warning("O CSV histórico não foi encontrado na pasta data.")
    else:
        historico_completo = carregar_historico(str(caminho_dados))
        # Filtra apenas a visualização. Não altera treino, modelo ou métricas.
        meses = {"Todo o período": None, "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5}
        periodo = st.selectbox("Período para explorar", list(meses), key="periodo_historico")
        dados_grafico = historico_completo.copy()
        if meses[periodo] is not None:
            dados_grafico = dados_grafico[dados_grafico["date"].dt.month == meses[periodo]].copy()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Registros no período", f"{len(dados_grafico):,}".replace(",", "."))
        m2.metric("Média por intervalo", f"{dados_grafico['Appliances'].mean():.1f} Wh")
        m3.metric("Mediana por intervalo", f"{dados_grafico['Appliances'].median():.1f} Wh")
        m4.metric("Maior consumo", f"{dados_grafico['Appliances'].max():.0f} Wh")

        with st.container(border=True):
            st.markdown("#### Evolução ao longo do período")
            # Calcula a média das medições de dez minutos em cada dia, não o total diário.
            media_diaria = dados_grafico.set_index("date")["Appliances"].resample("D").mean()
            serie = media_diaria.rename("Média por intervalo (Wh)").reset_index().rename(columns={"date": "Data"})
            st.line_chart(serie, x="Data", y="Média por intervalo (Wh)", color="#2dd4bf", height=280)
            st.caption("Cada ponto é a média dos intervalos de dez minutos daquele dia. Não representa a energia total do dia; os dias de início e fim podem ser parciais.")

        grafico_esquerdo, grafico_direito = st.columns(2, gap="large")
        with grafico_esquerdo:
            with st.container(border=True):
                st.markdown("#### Distribuição do consumo")
                # Agrupa todos os registros do período em faixas fixas de 50 Wh.
                # Envia somente as contagens ao gráfico, mantendo a tela leve.
                faixas = pd.cut(dados_grafico["Appliances"], bins=range(0, 1151, 50), right=False)
                frequencias = faixas.value_counts(sort=False)
                distribuicao = pd.DataFrame({
                    "Faixa (Wh)": [f"{int(faixa.left)}–{int(faixa.right)}" for faixa in frequencias.index],
                    "Registros": frequencias.values,
                })
                st.bar_chart(distribuicao, x="Faixa (Wh)", y="Registros", color="#a78bfa", sort=False, height=300)
                st.caption("As barras mostram quantos registros caem em cada faixa de 50 Wh; o limite superior de cada faixa é exclusivo.")

        with grafico_direito:
            with st.container(border=True):
                st.markdown("#### Dispersão · agora × próximo intervalo")
                # Seleciona pontos regularmente espaçados para evitar sobreposição excessiva.
                # O valor seguinte é observado na base; não é uma previsão do modelo.
                pares = dados_grafico.dropna(subset=["Consumo seguinte (Wh)"])
                amostra = pares.iloc[::10].rename(columns={"Appliances": "Consumo conhecido (Wh)"})
                st.scatter_chart(
                    amostra[["Consumo conhecido (Wh)", "Consumo seguinte (Wh)"]],
                    x="Consumo conhecido (Wh)", y="Consumo seguinte (Wh)",
                    color="#38bdf8", size=35, height=300,
                )
                st.caption(f"Cada ponto compara duas medições consecutivas reais. Exibidos {len(amostra)} pares, selecionando um a cada dez. Pontos iguais podem se sobrepor. O período filtra o horário da primeira medição.")

        with st.container(border=True):
            st.markdown("#### Perfil médio por hora")
            # Resume os registros disponíveis em cada hora do dia, de 0 a 23.
            media_horaria = dados_grafico.groupby(dados_grafico["date"].dt.hour)["Appliances"].mean()
            perfil = pd.DataFrame({"Hora": [f"{hora:02d}h" for hora in media_horaria.index], "Média por intervalo (Wh)": media_horaria.values})
            st.bar_chart(perfil, x="Hora", y="Média por intervalo (Wh)", color="#fbbf24", sort=False, height=220)
            st.caption("Média das medições de dez minutos em cada hora. Padrões históricos não garantem o comportamento futuro.")


with desempenho:
    st.subheader("Resultados reais, limites explícitos")
    st.write("A avaliação final usa um período posterior ao treino e à validação. Os resultados abaixo vêm do relatório gerado pelo projeto.")
    caminho_metricas = PASTA_PROJETO / "relatorios" / "metricas.csv"
    if caminho_metricas.is_file():
        metricas = pd.read_csv(caminho_metricas)
        linha = metricas[(metricas["conjunto"] == "teste") & (metricas["metodo"] == "regressao_linear")].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Erro absoluto médio · MAE", f"{linha['mae_wh']:.2f} Wh")
        c2.metric("Erro quadrático médio · MSE", f"{linha['mse_wh2']:.2f} Wh²")
        c3.metric("Coeficiente de determinação · R²", f"{linha['r2']:.4f}")
        st.info("O MAE é uma média dos erros no teste, não uma margem de confiança para cada previsão. R² não é percentual de acurácia.")
        st.dataframe(metricas.round(4), hide_index=True, width="stretch")
        st.caption("Limitação: a regressão linear reduziu MSE e melhorou R², mas a regra de repetir o último consumo teve MAE menor. Não há superioridade em todas as métricas.")
    else:
        st.info("O relatório de métricas ainda não está disponível nesta cópia do projeto.")

with sobre:
    st.subheader("Da medição à estimativa")
    a, b, c = st.columns(3)
    with a:
        st.markdown("#### 01 · Informar")
        st.write("O formulário reúne o consumo conhecido, a hora e o dia da semana.")
    with b:
        st.markdown("#### 02 · Processar")
        st.write("O FastAPI valida a entrada e consulta o pipeline já carregado na memória.")
    with c:
        st.markdown("#### 03 · Interpretar")
        st.write("A interface apresenta a estimativa recebida, com unidade e horizonte de previsão.")
    st.divider()
    st.markdown("**Fonte dos dados:** [Appliances Energy Prediction · UCI](https://doi.org/10.24432/C5VC8G), Luis Candanedo (2017), licença CC BY 4.0.")
    st.write("A base contém 19.735 medições de uma residência. A separação é cronológica e o alvo representa o consumo do registro seguinte, dez minutos depois.")
    st.caption("O modelo não identifica aparelhos individuais, não estima tarifas e não foi validado para qualquer residência. Não há monitoramento ao vivo nesta demonstração.")

st.markdown('<div class="footer">SCTEC · Projeto de Dados & IA &nbsp; / &nbsp; Interface Streamlit · API FastAPI · Modelo Scikit-learn</div>', unsafe_allow_html=True)
