# Registra detalhes de falhas no terminal do servidor.
import logging
from fastapi import APIRouter, HTTPException, Request
# Esquemas de entrada e saída da API.
from schemas import EntradaPrevisao, SaidaPrevisao, SaidaSaude
# Serviço que executa a previsão sem conhecer os códigos HTTP.
from services import prever_consumo

router = APIRouter()

# Cria o registrador de mensagens deste módulo.
logger = logging.getLogger(__name__)


# Consulta o serviço e verifica se existe um modelo na memória.
@router.get("/health", response_model=SaidaSaude)
def verificar_saude(request: Request):
    # Consulta o estado existente; não lê o arquivo nem treina o modelo.
    modelo_carregado = request.app.state.modelo is not None

    return {
        "status": "ativo",
        "modelo_carregado": modelo_carregado,
    }

# Recebe dados validados e devolve uma previsão no formato definido.
@router.post("/predict", response_model=SaidaPrevisao)
def realizar_previsao(entrada: EntradaPrevisao, request: Request):
    try:
        # Converte o esquema em dicionário e reutiliza o modelo da aplicação.
        resultado = prever_consumo(
            request.app.state.modelo,
            entrada.model_dump(),
        )

        # Valida também o conteúdo produzido antes de devolver a resposta.
        return SaidaPrevisao(previsao_wh=resultado)

    except ValueError as erro:
        # A solicitação não pôde produzir uma previsão válida para o domínio.
        raise HTTPException(status_code=400, detail=str(erro)) from erro

    except Exception as erro:
        # Guarda detalhes no servidor e devolve uma mensagem genérica ao cliente.
        logger.exception("Falha ao calcular a previsão.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível calcular a previsão.",
        ) from erro