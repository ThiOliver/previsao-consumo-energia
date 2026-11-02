# Previsão de Consumo de Energia

API de Machine Learning que estima o consumo dos aparelhos da residência estudada no próximo intervalo de **dez minutos**, em **Wh**. O objetivo é apoiar a análise do consumo de curto prazo, usando a última medição e o calendário conhecido. Projeto acadêmico SCTEC, desenvolvido em Python puro, com FastAPI e uma interface Streamlit opcional.

## Base e origem do modelo — opção B

Pipeline próprio treinado com a base pública **Appliances Energy Prediction**, de Luis Candanedo (2017), disponível no [UCI Machine Learning Repository](https://doi.org/10.24432/C5VC8G), sob [licença CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

A base foi escolhida por oferecer medições temporais reais e um alvo numérico adequado à regressão. O arquivo original está em `data/energydata_complete.csv`: 19.735 registros, 29 colunas, de 11/01/2016 às 17h a 27/05/2016 às 18h. A inspeção identificou horários únicos, ordenados e intervalos constantes de dez minutos. O CSV original é preservado.

O modelo usa `Appliances` (energia do intervalo concluído), `hora` e `dia_da_semana`. A resposta esperada, `consumo_futuro`, é a medição seguinte de `Appliances`. Hora e dia correspondem ao registro conhecido, não ao futuro. As demais colunas não entram nesta primeira versão, para manter um contrato simples e interpretável.

## Tecnologias e versões

Ambiente: Linux e Python **3.12.3**. As dependências da API, análise e testes estão fixadas em [requirements.txt](requirements.txt). As adicionais da interface estão em [requirements-interface.txt](requirements-interface.txt), que também instala as dependências principais.

| Tecnologia | Versão | Uso |
|---|---|---|
| pandas | 3.0.6 | Preparação e análise |
| NumPy | 2.5.4 | Operações numéricas |
| scikit-learn | 1.9.1 | Pipeline, modelos e métricas |
| joblib | 1.6.0 | Persistência |
| Matplotlib | 3.11.2 | Histograma |
| FastAPI | 0.162.0 | API |
| Pydantic | 2.14.1 | Contratos e validação |
| Uvicorn | 0.54.0 | Servidor ASGI |
| pytest | 9.2.0 | Testes |
| Streamlit (opcional) | 1.66.1 | Interface |
| Requests (opcional) | 2.34.2 | Comunicação da interface com a API |

## Instalação e execução

Em Linux, com Python 3.12 e Git instalados:

```bash
git clone https://github.com/ThiOliver/previsao-consumo-energia.git
cd previsao-consumo-energia
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

O modelo treinado acompanha o repositório: não é necessário treinar para usar a API. Execute os comandos a partir da raiz do projeto. Ao abrir outro terminal, ative novamente a `.venv`. Para encerrar um servidor, use `Ctrl+C` no terminal correspondente.

- [Swagger interativo](http://127.0.0.1:8000/docs)
- [Saúde da API](http://127.0.0.1:8000/health)
- [Contrato OpenAPI](http://127.0.0.1:8000/openapi.json)

Esses endereços funcionam **na máquina que está executando o projeto**. A entrega inclui execução local com Uvicorn; não há hospedagem pública configurada. O professor pode clonar e executar em sua própria máquina. Se aparecer `Address already in use`, confira se já existe uma API funcionando na porta 8000 ou encerre a execução anterior.

### Streamlit — complemento opcional

Mantenha a API aberta. Em outro terminal, dentro do projeto:

```bash
source .venv/bin/activate
python -m pip install -r requirements-interface.txt
python -m streamlit run interface.py
```

Abra [a interface local](http://localhost:8501). Se aparecer um pedido de e-mail no primeiro uso, pode deixar em branco e pressionar Enter.

A interface consulta a API, exibe gráficos históricos (linha, histograma, dispersão e médias por hora) e o relatório de métricas. Os gráficos ficam na aba **Explorar os dados**; representam observações históricas, não previsões.

A opção **Simular custo mensal** aparece após uma previsão. A fórmula é `(Wh previstos / 1000) × 6 × 24 × dias × tarifa em R$/kWh`. Ela supõe o mesmo consumo a cada dez minutos durante o mês inteiro. É uma extrapolação aritmética, não uma previsão mensal por IA nem o valor completo da conta. A tarifa é informada pelo usuário; não são acrescentados tributos, bandeiras ou cobranças fixas. A API funciona sem instalar ou iniciar o Streamlit.

## Fase 1 — preparação, treinamento e serialização

`analise_dados.py` verifica dimensões, tipos, sequência temporal e estatísticas, e gera `distribuicao_consumo.png`. `preparacao_dados.py` cria o alvo com `shift(-1)` e remove somente o registro final sem resposta futura. A separação mantém a ordem temporal, aproximadamente 70%/15%/15%, sem embaralhamento. Um exemplo em cada fronteira é excluído para que o alvo anterior não alcance as entradas do período seguinte.

| Conjunto | Exemplos | Início das entradas | Fim das entradas |
|---|---:|---|---|
| Treino | 13.812 | 11/01/2016 17:00 | 16/04/2016 14:50 |
| Validação | 2.959 | 16/04/2016 15:10 | 07/05/2016 04:10 |
| Teste | 2.961 | 07/05/2016 04:30 | 27/05/2016 17:50 |

Cada alvo ocorre dez minutos após a entrada. A preparação pressupõe os horários ordenados e regulares verificados na análise desta base.

O `ColumnTransformer` aplica imputação pela mediana e `StandardScaler` ao consumo; hora e dia recebem imputação pela categoria mais frequente e `OneHotEncoder`. A codificação evita tratar segunda-feira e domingo como uma distância numérica linear. Os imputadores tornam o pipeline preparado para ausências, embora não tenham sido encontradas na inspeção. Na API, campos ausentes são rejeitados. Todos os tratamentos aprendem **somente no treino**.

`treinamento.py` compara a referência de persistência (repetir o consumo conhecido), regressão linear e floresta aleatória. A floresta usa 100 árvores, profundidade máxima 10, mínimo de 5 exemplos por folha e semente 42. Após a comparação na validação, a regressão linear foi selecionada pelo menor MSE e maior R² entre os métodos avaliados, além da simplicidade. Essa escolha favorece a redução dos erros grandes; **a referência teve MAE melhor**. O período de teste foi reservado para avaliar a escolha, sem usá-lo para ajustar hiperparâmetros.

O artefato `models/pipeline_consumo.joblib` contém o pré-processamento e a regressão treinados. É o mesmo pipeline avaliado, sem retreino com validação ou teste. O script verifica a equivalência de uma previsão antes e depois de salvar.

### Métricas

| Conjunto | Método | MAE (Wh) ↓ | MSE (Wh²) ↓ | R² ↑ |
|---|---|---:|---:|---:|
| Validação | Referência | 26,16 | 4.414,26 | 0,4813 |
| Validação | Regressão linear | 27,95 | 3.831,84 | 0,5498 |
| Validação | Floresta aleatória | 28,10 | 3.885,87 | 0,5434 |
| Teste | Referência | 26,74 | 4.467,17 | 0,4590 |
| Teste | Regressão linear | 27,98 | 3.858,44 | 0,5328 |

Fonte: [relatorios/metricas.csv](relatorios/metricas.csv), com precisão completa.

- **MAE**: erro absoluto médio, em Wh. Facilita interpretar o tamanho médio dos erros; não é uma margem de confiança individual.
- **MSE**: erro quadrático médio, em Wh². Penaliza mais os erros grandes.
- **R²**: coeficiente de determinação; compara os erros quadráticos com uma previsão constante igual à média real do conjunto avaliado. Pode ser negativo e não é percentual de acurácia.

O modelo melhora MSE/R² em relação à referência, mas piora MAE. Não há superioridade em todos os critérios. Os resultados são de uma residência e período específicos, sem validação para outras residências. O modelo não prevê a conta inteira nem identifica aparelhos individualmente. Estimativas negativas são recusadas pela API.

### Reproduzir a etapa offline

```bash
python analise_dados.py
python preparacao_dados.py
python treinamento.py
```

Esses comandos regeneram o gráfico, o artefato e o CSV de métricas. O treinamento não acontece durante requisições da API. Após regenerar o modelo, reinicie o servidor para carregar a nova cópia.

## Fase 2 — arquitetura modular

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Cria a aplicação, gerencia lifespan e inclui o roteador |
| `routers.py` | Define endpoints com APIRouter e traduz erros para HTTP |
| `schemas.py` | Define entrada e saídas Pydantic |
| `services.py` | Carrega o pipeline e executa a inferência |
| `test_api.py` | Confere contratos, erros e carregamento único |
| `interface.py` | Interface opcional que consome a API |

## Fase 3 — lifespan

`main.py` usa `@asynccontextmanager`: carrega o artefato uma vez por inicialização da instância e guarda em `app.state.modelo`. As rotas reutilizam esse objeto em RAM. Não há leitura de `.joblib` ou treinamento em cada chamada. No encerramento, a referência é liberada. Se o arquivo estiver ausente, a inicialização falha com mensagem explícita. O caminho do artefato é calculado a partir do próprio módulo, sem diretórios pessoais fixos.

## Fase 4 — validação estrita

| Campo de entrada | Tipo | Regra |
|---|---|---|
| `Appliances` | Número | Finito e maior ou igual a zero, em Wh |
| `hora` | Inteiro | De 0 a 23 |
| `dia_da_semana` | Inteiro | De 0 a 6: segunda-feira a domingo |

Todos são obrigatórios. Texto em campo numérico, horas fracionárias, campos extras e valores fora dos limites são rejeitados antes da inferência. As saídas também têm esquemas próprios; a previsão deve ser finita e não negativa, unidade `Wh` e horizonte `10`.

## Fase 5 — endpoints e HTTP

### GET /health

Resposta HTTP 200:

```json
{"status": "ativo", "modelo_carregado": true}
```

### POST /predict

No Swagger, expanda a rota, clique em **Try it out**, preencha o **Request body** e clique em **Execute**:

```json
{"Appliances": 60, "hora": 17, "dia_da_semana": 0}
```

Resposta HTTP 200 (pequenas diferenças de ponto flutuante são possíveis):

```json
{"previsao_wh": 94.81619113478817, "unidade": "Wh", "horizonte_minutos": 10}
```

Exemplo no terminal, com a API aberta:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"Appliances": 60, "hora": 17, "dia_da_semana": 0}'
```

| Código | Situação |
|---|---|
| 200 | Consulta ou previsão concluída |
| 400 | Entradas válidas, mas previsão negativa, incompatível com energia |
| 422 | Dados de entrada inválidos; por exemplo, `hora: 24` |
| 500 | Falha interna ou saída inválida; mensagem genérica ao cliente, detalhes no log |

## Verificação

```bash
python -m pytest -q test_api.py
python -m pip check
```

Foram verificados 15 testes da API e 2 da interface opcional. Para executar também a interface, instale `requirements-interface.txt` e use `python -m pytest -q test_interface.py`.

Os testes incluem previsão real, entradas inválidas impedidas de alcançar o modelo, previsão negativa, falhas internas, validação de saída e carregamento único. O aviso de depreciação de `httpx` no TestClient é uma orientação de migração da dependência e não equivale a falha de teste.

## Desenvolvimento e melhorias possíveis

As etapas foram organizadas em ambiente, dados, análise, preparação, treinamento, API e interface, usando `feature/*` e integração em `develop`. As branches são preservadas após os PRs. A publicação final em `main` deve ocorrer após inserir o link do vídeo.

Melhorias futuras: testar mais variáveis e defasagens com validação temporal, investigar picos, obter dados de outras residências, medir incerteza e configurar hospedagem pública com monitoramento. Mudanças de modelo exigem nova avaliação; os dados futuros não podem entrar no treino.

## Vídeo de apresentação

**PENDENTE: inserir aqui o link real do vídeo no Google Drive antes do merge em main e da entrega.**

O vídeo deve ter até dez minutos, com acesso de leitor para qualquer pessoa com o link. Confira a abertura sem login e envie os links do vídeo e do repositório no AVA. Após a entrega, mantenha o repositório sem alterações até a avaliação, conforme o PDF.
