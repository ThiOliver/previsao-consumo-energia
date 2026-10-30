# Ferramentas para executar testes e simular situações controladas.
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app
from services import carregar_modelo


# Fornece uma aplicação inicializada para cada teste.
# O contexto executa o lifespan na abertura e no encerramento.
@pytest.fixture
def cliente():
    with TestClient(app) as client:
        yield client


# Confere o estado real do serviço e a estrutura da resposta.
def test_health(cliente):
    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ativo",
        "modelo_carregado": True,
    }


# Confere uma previsão válida com o pipeline real.
def test_previsao_valida(cliente):
    resposta = cliente.post("/predict", json={
        "Appliances": 60,
        "hora": 17,
        "dia_da_semana": 0,
    })

    assert resposta.status_code == 200

    dados = resposta.json()
    assert set(dados) == {"previsao_wh", "unidade", "horizonte_minutos"}
    assert dados["previsao_wh"] == pytest.approx(94.81619113478817)
    assert dados["unidade"] == "Wh"
    assert dados["horizonte_minutos"] == 10


# Repete o teste com diferentes entradas inválidas.
@pytest.mark.parametrize("alteracao", [
    {"hora": 24},
    {"hora": 1.5},
    {"dia_da_semana": 7},
    {"Appliances": -1},
    {"Appliances": "60"},
    {"campo_extra": 10},
])
def test_entrada_invalida(cliente, alteracao):
    entrada = {"Appliances": 60, "hora": 17, "dia_da_semana": 0}
    entrada.update(alteracao)

    # Confirma que dados inválidos nem chegam ao serviço de previsão.
    with patch("routers.prever_consumo") as prever:
        resposta = cliente.post("/predict", json=entrada)

        assert resposta.status_code == 422
        prever.assert_not_called()


# Simula uma previsão negativa sem modificar o modelo salvo.
def test_previsao_negativa(cliente):
    with patch.object(app.state.modelo, "predict", return_value=[-1.0]):
        resposta = cliente.post("/predict", json={
            "Appliances": 60,
            "hora": 17,
            "dia_da_semana": 0,
        })

    assert resposta.status_code == 400
    assert "estimativa não negativa" in resposta.json()["detail"]


# Simula uma falha interna e verifica se detalhes técnicos ficam ocultos.
def test_falha_interna(cliente):
    with patch(
        "routers.prever_consumo",
        side_effect=RuntimeError("detalhe interno de teste"),
    ):
        resposta = cliente.post("/predict", json={
            "Appliances": 60,
            "hora": 17,
            "dia_da_semana": 0,
        })

    assert resposta.status_code == 500
    assert resposta.json() == {
        "detail": "Não foi possível calcular a previsão.",
    }

    # Após a falha simulada, a aplicação continua atendendo.
    assert cliente.get("/health").status_code == 200


# Confere o carregamento único e impede novas leituras do artefato nas rotas.
def test_carregamento_unico():
    with patch("main.carregar_modelo", wraps=carregar_modelo) as carregar:
        with TestClient(app) as client:
            modelo_inicial = app.state.modelo

            # Qualquer tentativa de recarregar o arquivo agora causa erro.
            with patch(
                "services.joblib.load",
                side_effect=RuntimeError("Recarga indevida"),
            ):
                for _ in range(3):
                    assert client.get("/health").status_code == 200

                    resposta = client.post("/predict", json={
                        "Appliances": 60,
                        "hora": 17,
                        "dia_da_semana": 0,
                    })
                    assert resposta.status_code == 200

            carregar.assert_called_once()
            assert app.state.modelo is modelo_inicial

        # Confere a limpeza após encerrar o ciclo da aplicação.
        assert app.state.modelo is None