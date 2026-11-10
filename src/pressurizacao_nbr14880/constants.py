"""Constantes e parâmetros normativos da ABNT NBR 14880:2014.

ABNT NBR 14880:2014 - Saídas de emergência em edifícios -
Sistemas de pressurização de escadas.
"""

from fractions import Fraction
from typing import Final

# Diferenciais de pressão regulamentares (Pascal)
PRESSAO_DIFERENCIAL_MINIMA_PA: Final[Fraction] = Fraction(50, 1)  # 50 Pa com portas fechadas
PRESSAO_DIFERENCIAL_MAXIMA_PA: Final[Fraction] = Fraction(60, 1)  # 60 Pa para limitar força em 110 N
FORCA_MAXIMA_ABERTURA_PORTA_N: Final[Fraction] = Fraction(110, 1)  # 110 N na maçaneta

# Velocidades de escape do ar através de portas abertas (m/s)
VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S: Final[Fraction] = Fraction(1, 1)  # 1.00 m/s
VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S: Final[Fraction] = Fraction(1, 1)  # 1.00 m/s (mínimo)
VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S: Final[Fraction] = Fraction(2, 1)  # 2.00 m/s

# Fator específico de vazamento por fresta sob 50 Pa: 0.827 * sqrt(50) ~= 5.85 m³/(s*m²)
COEFICIENTE_VAZAMENTO_FRESTA_50PA: Final[Fraction] = Fraction(117, 20)  # 5.85 m³/(s*m²)

# Áreas típicas de frestas perimetrais de portas corta-fogo fechadas (m²)
AREA_FRESTA_PORTA_SIMPLES_M2: Final[Fraction] = Fraction(21, 1000)  # 0.021 m² (0.90m x 2.10m)
AREA_FRESTA_PORTA_DUPLA_M2: Final[Fraction] = Fraction(35, 1000)  # 0.035 m² (1.80m x 2.10m)

# Dimensões nominais de passagem livre de portas corta-fogo padrão
LARGURA_PORTA_PADRAO_M: Final[Fraction] = Fraction(9, 10)  # 0.90 m
ALTURA_PORTA_PADRAO_M: Final[Fraction] = Fraction(21, 10)  # 2.10 m
AREA_PASSAGEM_PORTA_PADRAO_M2: Final[Fraction] = Fraction(189, 100)  # 1.89 m²

# Fatores de majoração e segurança normativos
FATOR_MAJORACAO_VAZAMENTOS_DUTO: Final[Fraction] = Fraction(23, 20)  # 1.15 (+15% no duto e conexões)
FATOR_SEGURANCA_VENTILADOR: Final[Fraction] = Fraction(5, 4)  # 1.25 (+25% margem global)

# Limites de velocidade do ar em dutos e grelhas (m/s)
VELOCIDADE_MAX_DUTO_METALICO_M_S: Final[Fraction] = Fraction(15, 1)  # 15.0 m/s
VELOCIDADE_MAX_DUTO_ALVENARIA_M_S: Final[Fraction] = Fraction(10, 1)  # 10.0 m/s
VELOCIDADE_MAX_GRELHA_INSUFLAMENTO_M_S: Final[Fraction] = Fraction(5, 1)  # 5.0 m/s

# Parâmetros de ventiladores centrífugos e motores elétricos
RENDIMENTO_PADRAO_VENTILADOR: Final[Fraction] = Fraction(70, 100)  # 70% de rendimento aerodinâmico
MARGEM_SEGURANCA_MOTOR: Final[Fraction] = Fraction(23, 20)  # 1.15 (+15% de sobrepotência do motor)
CONVERSAO_WATT_PARA_CV: Final[Fraction] = Fraction(2, 1471)  # 1 cv = 735.5 W (1471/2)

# Potências comerciais padronizadas de motores trifásicos em cv (WEG / NEMA)
MOTORES_COMERCIAIS_CV: Final[tuple[Fraction, ...]] = (
    Fraction(1, 1),      # 1.0 cv
    Fraction(15, 10),    # 1.5 cv
    Fraction(2, 1),      # 2.0 cv
    Fraction(3, 1),      # 3.0 cv
    Fraction(4, 1),      # 4.0 cv
    Fraction(5, 1),      # 5.0 cv
    Fraction(75, 10),    # 7.5 cv
    Fraction(10, 1),     # 10.0 cv
    Fraction(15, 1),     # 15.0 cv
    Fraction(20, 1),     # 20.0 cv
    Fraction(25, 1),     # 25.0 cv
    Fraction(30, 1),     # 30.0 cv
    Fraction(40, 1),     # 40.0 cv
    Fraction(50, 1),     # 50.0 cv
    Fraction(60, 1),     # 60.0 cv
    Fraction(75, 1),     # 75.0 cv
)
