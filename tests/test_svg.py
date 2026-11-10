"""Testes do gerador vetorial SVG para pressurização de escadas NBR 14880."""

import unittest
from fractions import Fraction

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    TipoDuto,
    TipoEscada,
)
from pressurizacao_nbr14880.svg_generator import gerar_painel_svg


class TestSVGGenerator(unittest.TestCase):
    """Verifica a integridade do XML/SVG 1440x900 gerado."""

    def setUp(self) -> None:
        self.dados = DadosEdificacao(
            nome_edificio="Edifício Teste SVG",
            quantidade_pavimentos=15,
            altura_total_m=Fraction(45, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=15,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(250, 1),
        )
        self.res = dimensionar_pressurizacao_escada(self.dados)

    def test_svg_dimensoes_e_namespaces(self) -> None:
        svg = gerar_painel_svg(self.res)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn('viewBox="0 0 1440 900"', svg)
        self.assertIn('xmlns="http://www.w3.org/2000/svg"', svg)

    def test_svg_elementos_obrigatorios(self) -> None:
        svg = gerar_painel_svg(self.res)
        self.assertIn("ABNT NBR 14880:2014", svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("Edifício Teste SVG", svg)
        self.assertIn("VENTILADOR CENTRÍFUGO", svg)
        self.assertIn("Caixa de Escada Pressurizada (+50 Pa)", svg)


if __name__ == "__main__":
    unittest.main()
