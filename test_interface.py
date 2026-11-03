# Estes testes são opcionais: sem Streamlit instalado, o pytest os ignora.
from unittest.mock import Mock, patch

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest


# Simula respostas HTTP para conferir a tela sem depender de um servidor aberto.
def resposta_json(conteudo):
    resposta = Mock()
    resposta.status_code = 200
    resposta.json.return_value = conteudo
    return resposta


# Confere a previsão exibida e a fórmula mensal com uma tarifa apenas de teste.
def test_simulacao_mensal():
    with patch("requests.get", return_value=resposta_json({"status": "ativo", "modelo_carregado": True})), patch(
        "requests.post", return_value=resposta_json({"previsao_wh": 100.0, "unidade": "Wh", "horizonte_minutos": 10})
    ) as enviar:
        tela = AppTest.from_file("interface.py").run(timeout=30)
        assert not tela.exception
        next(botao for botao in tela.button if "Calcular" in botao.label).click().run()
        next(campo for campo in tela.number_input if "Tarifa" in campo.label).set_value(1.0).run()
        assert not tela.exception
        valores = {metrica.label: metrica.value for metrica in tela.metric}
        assert valores["Energia mensal simulada"] == "432.00 kWh"
        assert valores["Custo mensal simulado"] == "R$ 432.00"
        # Alterar a tarifa não envia uma nova previsão à API.
        assert enviar.call_count == 1


# Uma falha de conexão deve produzir uma mensagem, não derrubar a página.
def test_interface_sem_api():
    import requests

    with patch("requests.get", side_effect=requests.exceptions.ConnectionError), patch(
        "requests.post", side_effect=requests.exceptions.ConnectionError
    ):
        tela = AppTest.from_file("interface.py").run(timeout=30)
        next(botao for botao in tela.button if "Calcular" in botao.label).click().run()
        assert not tela.exception
        assert any("conectar" in mensagem.value for mensagem in tela.error)
        assert tela.session_state.ultima_previsao is None
