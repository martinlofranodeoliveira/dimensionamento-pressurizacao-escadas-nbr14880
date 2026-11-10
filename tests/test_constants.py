"""Testes unitários das constantes normativas da ABNT NBR 14880:2014."""

import unittest
from fractions import Fraction

from pressurizacao_nbr14880.constants import (
    AREA_FRESTA_PORTA_DUPLA_M2,
    AREA_FRESTA_PORTA_SIMPLES_M2,
    AREA_PASSAGEM_PORTA_PADRAO_M2,
    COEFICIENTE_VAZAMENTO_FRESTA_50PA,
    CONVERSAO_WATT_PARA_CV,
    FATOR_MAJORACAO_VAZAMENTOS_DUTO,
    FATOR_SEGURANCA_VENTILADOR,
    FORCA_MAXIMA_ABERTURA_PORTA_N,
    LARGURA_PORTA_PADRAO_M,
    MARGEM_SEGURANCA_MOTOR,
    MOTORES_COMERCIAIS_CV,
    PRESSAO_DIFERENCIAL_MAXIMA_PA,
    PRESSAO_DIFERENCIAL_MINIMA_PA,
    RENDIMENTO_PADRAO_VENTILADOR,
    VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S,
    VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S,
    VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S,
    VELOCIDADE_MAX_DUTO_ALVENARIA_M_S,
    VELOCIDADE_MAX_DUTO_METALICO_M_S,
)


class TestConstants(unittest.TestCase):
    """Verifica a conformidade rigorosa das constantes com a NBR 14880:2014."""

    def test_diferenciais_de_pressao(self) -> None:
        self.assertEqual(PRESSAO_DIFERENCIAL_MINIMA_PA, Fraction(50, 1))
        self.assertEqual(PRESSAO_DIFERENCIAL_MAXIMA_PA, Fraction(60, 1))
        self.assertEqual(FORCA_MAXIMA_ABERTURA_PORTA_N, Fraction(110, 1))

    def test_velocidades_de_escape(self) -> None:
        self.assertEqual(VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S, Fraction(1, 1))
        self.assertEqual(VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S, Fraction(1, 1))
        self.assertEqual(VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S, Fraction(2, 1))

    def test_frestas_e_geometria_portas(self) -> None:
        self.assertEqual(AREA_FRESTA_PORTA_SIMPLES_M2, Fraction(21, 1000))
        self.assertEqual(AREA_FRESTA_PORTA_DUPLA_M2, Fraction(35, 1000))
        self.assertEqual(AREA_PASSAGEM_PORTA_PADRAO_M2, Fraction(189, 100))
        self.assertEqual(COEFICIENTE_VAZAMENTO_FRESTA_50PA, Fraction(117, 20))

    def test_dutos_e_velocidades(self) -> None:
        self.assertEqual(VELOCIDADE_MAX_DUTO_METALICO_M_S, Fraction(15, 1))
        self.assertEqual(VELOCIDADE_MAX_DUTO_ALVENARIA_M_S, Fraction(10, 1))
        self.assertEqual(FATOR_MAJORACAO_VAZAMENTOS_DUTO, Fraction(23, 20))
        self.assertEqual(FATOR_SEGURANCA_VENTILADOR, Fraction(5, 4))

    def test_ventilador_e_motores(self) -> None:
        self.assertEqual(RENDIMENTO_PADRAO_VENTILADOR, Fraction(70, 100))
        self.assertEqual(MARGEM_SEGURANCA_MOTOR, Fraction(23, 20))
        self.assertTrue(len(MOTORES_COMERCIAIS_CV) >= 10)
        self.assertEqual(MOTORES_COMERCIAIS_CV[0], Fraction(1, 1))


if __name__ == "__main__":
    unittest.main()
