"""Testes unitários do codec JSON canônico RFC 8259 da NBR 14880."""

import json
import unittest
from fractions import Fraction

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.codecs import (
    carregar_dados_edificacao_json,
    exportar_resultado_json,
)
from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    TipoDuto,
    TipoEscada,
)


class TestCodecs(unittest.TestCase):
    """Validação estrita do codec JSON canônico sem ponto flutuante."""

    def test_carregar_dados_valido(self) -> None:
        json_str = """{
            "nome_edificio": "Prédio Teste",
            "quantidade_pavimentos": 12,
            "altura_total_m": "36.0",
            "tipo_escada": "enclausurada_protegida",
            "tipo_duto": "metalico_galvanizado",
            "possui_sprinklers": true,
            "quantidade_portas_simples": 12,
            "quantidade_portas_duplas": 0,
            "portas_abertas_projeto": 2,
            "perda_carga_distribuicao_pa": "250"
        }"""
        dados = carregar_dados_edificacao_json(json_str)
        self.assertEqual(dados.nome_edificio, "Prédio Teste")
        self.assertEqual(dados.quantidade_pavimentos, 12)
        self.assertEqual(dados.altura_total_m, Fraction(36, 1))

    def test_rejeitar_bom(self) -> None:
        json_bom = "\ufeff" + '{"nome_edificio": "Teste"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_edificacao_json(json_bom)
        self.assertIn("BOM", str(ctx.exception))

    def test_rejeitar_chaves_duplicadas(self) -> None:
        json_dup = '{"nome_edificio": "A", "nome_edificio": "B"}'
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_edificacao_json(json_dup)
        self.assertIn("duplicada", str(ctx.exception).lower())

    def test_rejeitar_ponto_flutuante(self) -> None:
        json_float = '{"nome_edificio": "Teste", "altura_total_m": 36.5}'
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_edificacao_json(json_float)
        self.assertIn("Ponto flutuante", str(ctx.exception))

    def test_rejeitar_profundidade_excessiva(self) -> None:
        profundo: dict = {"nivel": 0}
        atual = profundo
        for i in range(35):
            atual["sub"] = {"nivel": i + 1}
            atual = atual["sub"]
        json_profundo = json.dumps(profundo)
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_edificacao_json(json_profundo)
        self.assertIn("Profundidade", str(ctx.exception))

    def test_rejeitar_raiz_lista(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            carregar_dados_edificacao_json("[]")
        self.assertIn("dicionário", str(ctx.exception))

    def test_exportar_json_resultado(self) -> None:
        dados = DadosEdificacao(
            nome_edificio="Serializacao",
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
        res = dimensionar_pressurizacao_escada(dados)
        res_json = exportar_resultado_json(res)
        self.assertIn("ABNT NBR 14880:2014", res_json)
        self.assertIn("Serializacao", res_json)
        self.assertIn("estagio1", res_json)
        self.assertIn("estagio2", res_json)
        self.assertIn("ventilador", res_json)


if __name__ == "__main__":
    unittest.main()
