# Literal restringe um campo a valores específicos.
from typing import Literal

# Pydantic define os formatos e verifica os dados.
from pydantic import BaseModel, ConfigDict, Field


# Define as informações recebidas para calcular uma previsão.
class EntradaPrevisao(BaseModel):
    # Rejeita conversões de texto para número, campos extras e números não finitos.
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    Appliances: float = Field(
        ge=0,
        description="Energia do último intervalo concluído, em Wh.",
    )

    hora: int = Field(
        ge=0,
        le=23,
        description="Hora do registro conhecido, de 0 a 23.",
    )

    dia_da_semana: int = Field(
        ge=0,
        le=6,
        description="Dia do registro conhecido: segunda-feira é 0 e domingo é 6.",
    )


# Define o formato da resposta de previsão.
class SaidaPrevisao(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    previsao_wh: float = Field(
        description="Estimativa de energia para o próximo intervalo de dez minutos.",
    )

    unidade: Literal["Wh"] = "Wh"
    horizonte_minutos: Literal[10] = 10


# Define o formato da resposta de monitoramento.
class SaidaSaude(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    status: Literal["ativo"]
    modelo_carregado: bool