# Permite definir as etapas de abertura e encerramento da aplicação.
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Importa as rotas e o serviço responsável por recuperar o pipeline.
from routers import router
from services import carregar_modelo


# Executa o carregamento uma vez por instância da aplicação.
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.modelo = carregar_modelo()
    print("Modelo carregado na memória.")

    # Entrega o controle ao servidor para atender às requisições.
    try:
        yield
    finally:
        # Remove a referência ao modelo quando a aplicação encerra.
        app.state.modelo = None


# Configura a aplicação e associa seu ciclo de vida.
app = FastAPI(
    title="API de Previsão de Consumo de Energia",
    description="Previsão do consumo dos aparelhos no próximo intervalo de dez minutos.",
    version="0.1.0",
    lifespan=lifespan,
)

# Registra as rotas definidas no módulo próprio.
app.include_router(router)