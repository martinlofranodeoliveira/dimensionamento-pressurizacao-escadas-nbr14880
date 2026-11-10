"""Motor de dimensionamento de pressurização de escadas ABNT NBR 14880:2014."""

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.codecs import (
    carregar_dados_edificacao_json,
    exportar_resultado_json,
)
from pressurizacao_nbr14880.constants import (
    FORCA_MAXIMA_ABERTURA_PORTA_N,
    MOTORES_COMERCIAIS_CV,
    PRESSAO_DIFERENCIAL_MAXIMA_PA,
    PRESSAO_DIFERENCIAL_MINIMA_PA,
    VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S,
    VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S,
    VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S,
    VELOCIDADE_MAX_DUTO_ALVENARIA_M_S,
    VELOCIDADE_MAX_DUTO_METALICO_M_S,
)
from pressurizacao_nbr14880.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    ResultadoDimensionamento,
    ResultadoDuto,
    ResultadoEstagio1,
    ResultadoEstagio2,
    ResultadoVentilador,
    TipoDuto,
    TipoEscada,
    TipoPorta,
)
from pressurizacao_nbr14880.svg_generator import gerar_painel_svg

__version__ = "1.0.0"

__all__ = [
    "DadosEdificacao",
    "ResultadoDimensionamento",
    "ResultadoDuto",
    "ResultadoEstagio1",
    "ResultadoEstagio2",
    "ResultadoVentilador",
    "TipoDuto",
    "TipoEscada",
    "TipoPorta",
    "FORCA_MAXIMA_ABERTURA_PORTA_N",
    "MOTORES_COMERCIAIS_CV",
    "PRESSAO_DIFERENCIAL_MAXIMA_PA",
    "PRESSAO_DIFERENCIAL_MINIMA_PA",
    "VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S",
    "VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S",
    "VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S",
    "VELOCIDADE_MAX_DUTO_ALVENARIA_M_S",
    "VELOCIDADE_MAX_DUTO_METALICO_M_S",
    "carregar_dados_edificacao_json",
    "dimensionar_pressurizacao_escada",
    "exportar_resultado_json",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip",
    "gerar_painel_svg",
    "gerar_relatorio_texto",
]
