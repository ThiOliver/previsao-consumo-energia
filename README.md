# Previsão de Consumo de Energia

Projeto acadêmico de desenvolvimento de uma API para previsão de
consumo de energia com Python e Machine Learning.

## Objetivo

Prever a energia consumida pelos aparelhos da residência estudada
no próximo intervalo de 10 minutos, em watt-hora (Wh), utilizando
informações disponíveis antes desse intervalo.

## Base de dados

A base selecionada é Appliances Energy Prediction, disponibilizada
pelo UCI Machine Learning Repository.

- Autor: Luis Candanedo.
- Ano de publicação: 2017.
- Fonte: https://doi.org/10.24432/C5VC8G
- Licença: Creative Commons Attribution 4.0 International (CC BY 4.0).
- Licença completa: https://creativecommons.org/licenses/by/4.0/

A inspeção e os tratamentos dos dados ainda não foram realizados.
As transformações aplicadas serão documentadas durante o desenvolvimento.

## Solução planejada

- Examinar e preparar os dados.
- Separar os dados cronologicamente em treino, validação e teste.
- Treinar e avaliar um modelo de regressão.
- Salvar o pipeline treinado.
- Disponibilizar previsões por uma API FastAPI.
- Validar entradas e saídas com Pydantic.
- Implementar GET /health e POST /predict.

Uma interface com Streamlit será considerada após a conclusão
e validação dos requisitos obrigatórios.

## Tecnologias previstas

- Python.
- FastAPI.
- Pydantic.
- Uvicorn.
- Git e GitHub.

As bibliotecas de análise de dados, treinamento e persistência,
assim como suas versões, serão registradas após sua definição.

## Estado atual

Projeto em preparação. Ainda não há modelo treinado nem API implementada.

## Instalação e execução

### Preparação do ambiente local

Ambiente verificado em Linux com Python 3.12.3.

No terminal, dentro da pasta do projeto, crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente:

```bash
source .venv/bin/activate
```

Confira o Python e o instalador de bibliotecas utilizados:

```bash
which python
python --version
python -m pip --version
```

Os caminhos do Python e do pip devem apontar para a pasta `.venv`
do projeto.

Ao abrir um novo terminal, ative novamente o ambiente.
Não é necessário recriá-lo.

A pasta `.venv` é local e não é versionada pelo Git.

### Dependências e aplicação

As dependências do projeto ainda não foram instaladas.
As instruções de instalação e execução da API serão adicionadas
conforme o desenvolvimento avançar.

## Documentação da API

Os exemplos de entrada e saída e o endereço da documentação Swagger
serão adicionados após a implementação.

## Apresentação

O link do vídeo será incluído antes da entrega.