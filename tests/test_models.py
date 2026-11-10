"""Testes dos modelos de dados imutáveis da NBR 14880."""

import unittest
from fractions import Fraction

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


class TestModels(unittest.TestCase):
    """Testa dataclasses imutáveis e enums do modelo."""

    def test_enums(self) -> None:
        self.assertEqual(TipoEscada.ENCLAUSURADA_PROTEGIDA.value, "enclausurada_protegida")
        self.assertEqual(TipoEscada.COM_ANTECAMARA.value, "com_antecamara")
        self.assertEqual(TipoEscada.PRESSURIZADA_DIRETA.value, "pressurizada_direta")
        self.assertEqual(TipoDuto.METALICO_GALVANIZADO.value, "metalico_galvanizado")
        self.assertEqual(TipoPorta.SIMPLES_PADRAO.value, "simples_padrao")

    def test_dados_edificacao_imutabilidade(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Torre Alta",
            quantidade_pavimentos=20,
            altura_total_m=Fraction(60, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=20,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(250, 1),
        )
        self.assertEqual(dados.nome_edificio, "Torre Alta")
        with self.assertRaises(Exception):
            dados.quantidade_pavimentos = 25  # type: ignore

    def test_resultado_estagio1_instanciacao(self) -> None:
        res = ResultadoEstagio1(
            pressao_diferencial_pa=Fraction(50, 1),
            area_total_frestas_m2=Fraction(42, 100),
            vazao_frestas_m3_s=Fraction(2457, 1000),
            vazao_frestas_m3_h=Fraction(8845, 1),
        )
        self.assertEqual(res.pressao_diferencial_pa, Fraction(50, 1))


if __name__ == "__main__":
    unittest.main()
