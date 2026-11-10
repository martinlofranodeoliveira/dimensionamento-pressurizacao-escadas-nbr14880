"""Testes unitários do motor de cálculo de pressurização de escadas NBR 14880."""

import unittest
from fractions import Fraction

from pressurizacao_nbr14880.calculator import _teto_fracao, dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.constants import (
    FORCA_MAXIMA_ABERTURA_PORTA_N,
    PRESSAO_DIFERENCIAL_MINIMA_PA,
    VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S,
    VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S,
)
from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    TipoDuto,
    TipoEscada,
)


class TestCalculator(unittest.TestCase):
    """Testa os cálculos de aerodinâmica, vazões e sobrepressão."""

    def test_teto_fracao(self) -> None:
        self.assertEqual(_teto_fracao(Fraction(10, 1)), 10)
        self.assertEqual(_teto_fracao(Fraction(0, 1)), 0)
        self.assertEqual(_teto_fracao(Fraction(7, 2)), 4)
        self.assertEqual(_teto_fracao(Fraction(1, 5)), 1)
        self.assertEqual(_teto_fracao(Fraction(25, 4)), 7)

    def test_estagio1_portas_fechadas(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Prédio Baixo",
            quantidade_pavimentos=6,
            altura_total_m=Fraction(18, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=6,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertEqual(res.estagio1.pressao_diferencial_pa, PRESSAO_DIFERENCIAL_MINIMA_PA)
        # 6 * 0.021 = 0.126 m²
        self.assertEqual(res.estagio1.area_total_frestas_m2, Fraction(126, 1000))
        # 0.126 * 5.85 = 0.7371 m³/s
        self.assertEqual(res.estagio1.vazao_frestas_m3_s, Fraction(126, 1000) * Fraction(117, 20))
        self.assertTrue(res.estagio1.vazao_frestas_m3_h > 0)

    def test_estagio2_com_sprinklers(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Edifício Sprinklers",
            quantidade_pavimentos=8,
            altura_total_m=Fraction(24, 1),
            tipo_escada=TipoEscada.COM_ANTECAMARA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=8,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertEqual(res.estagio2.velocidade_escape_m_s, VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S)
        self.assertEqual(res.estagio2.portas_abertas, 1)
        self.assertGreater(res.estagio2.vazao_total_estagio2_m3_s, res.estagio1.vazao_frestas_m3_s)

    def test_estagio2_rota_critica_sem_sprinklers(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Escada Direta",
            quantidade_pavimentos=5,
            altura_total_m=Fraction(15, 1),
            tipo_escada=TipoEscada.PRESSURIZADA_DIRETA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=False,
            quantidade_portas_simples=5,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertEqual(res.estagio2.velocidade_escape_m_s, VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S)

    def test_ajuste_portas_abertas_edificio_alto(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Torre Alta",
            quantidade_pavimentos=20,
            altura_total_m=Fraction(60, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=20,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,  # Abaixo do mínimo de 2
            perda_carga_distribuicao_pa=Fraction(250, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertEqual(res.estagio2.portas_abertas, 2)
        self.assertTrue(any("exige no mínimo 2 portas abertas" in a for a in res.alertas))

    def test_duto_alvenaria_adota_velocidade_menor(self) -> None:
        dados_met = DadosEdificacao(
            nome_edificio="Metálico",
            quantidade_pavimentos=10,
            altura_total_m=Fraction(30, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=10,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        dados_alv = DadosEdificacao(
            nome_edificio="Alvenaria",
            quantidade_pavimentos=10,
            altura_total_m=Fraction(30, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.ALVENARIA_CONCRETO,
            possui_sprinklers=True,
            quantidade_portas_simples=10,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        res_met = dimensionar_pressurizacao_escada(dados_met)
        res_alv = dimensionar_pressurizacao_escada(dados_alv)

        self.assertEqual(res_met.duto.velocidade_adotada_m_s, Fraction(12, 1))
        self.assertEqual(res_alv.duto.velocidade_adotada_m_s, Fraction(8, 1))
        # Duto de alvenaria precisa de área maior devido à velocidade menor
        self.assertGreater(res_alv.duto.area_util_minima_m2, res_met.duto.area_util_minima_m2)

    def test_forca_abertura_porta_conforme(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Força Normal",
            quantidade_pavimentos=12,
            altura_total_m=Fraction(36, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=12,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(250, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertTrue(res.conformidade_forca_abertura)
        self.assertLessEqual(res.forca_abertura_porta_n, FORCA_MAXIMA_ABERTURA_PORTA_N)

    def test_selecao_motor_comercial(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Motor Teste",
            quantidade_pavimentos=15,
            altura_total_m=Fraction(45, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=15,
            quantidade_portas_duplas=1,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(300, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertGreater(res.ventilador.motor_comercial_adotado_cv, 0)
        self.assertGreaterEqual(
            res.ventilador.motor_comercial_adotado_cv,
            res.ventilador.potencia_motor_calculada_cv,
        )

    def test_recomendacoes_conteudo(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Recs",
            quantidade_pavimentos=8,
            altura_total_m=Fraction(24, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=8,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        res = dimensionar_pressurizacao_escada(dados)
        self.assertTrue(any("ABNT NBR 14880:2014" in r for r in res.recomendacoes))
        self.assertTrue(any("50 Pa" in r for r in res.recomendacoes))


if __name__ == "__main__":
    unittest.main()
