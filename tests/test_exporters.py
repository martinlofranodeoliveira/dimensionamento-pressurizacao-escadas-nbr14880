"""Testes unitários dos exportadores técnicos da NBR 14880."""

import os
import tempfile
import unittest
import zipfile
from fractions import Fraction

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.exporters import (
    _fmt,
    _sanitizar_campo_csv,
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    TipoDuto,
    TipoEscada,
)


class TestExporters(unittest.TestCase):
    """Testa memorial de texto, sanitização CSV e empacotamento determinístico ZIP."""

    def setUp(self) -> None:
        self.dados = DadosEdificacao(
            nome_edificio="=FormulaPerigo",
            quantidade_pavimentos=14,
            altura_total_m=Fraction(42, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=14,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(250, 1),
        )
        self.res = dimensionar_pressurizacao_escada(self.dados)

    def test_fmt_sem_float(self) -> None:
        self.assertEqual(_fmt(Fraction(15, 1), 2), "15.0")
        self.assertEqual(_fmt(Fraction(15, 2), 2), "7.50")
        self.assertEqual(_fmt(Fraction(1, 4), 2), "0.25")

    def test_sanitizar_campo_csv(self) -> None:
        self.assertEqual(_sanitizar_campo_csv("=1+1"), "'=1+1")
        self.assertEqual(_sanitizar_campo_csv("+cmd"), "'+cmd")
        self.assertEqual(_sanitizar_campo_csv("-100"), "'-100")
        self.assertEqual(_sanitizar_campo_csv("@calc"), "'@calc")
        self.assertEqual(_sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(_sanitizar_campo_csv("normal"), "normal")

    def test_gerar_relatorio_texto(self) -> None:
        txt = gerar_relatorio_texto(self.res)
        self.assertIn("ABNT NBR 14880:2014", txt)
        self.assertIn("ESTÁGIO 1", txt)
        self.assertIn("ESTÁGIO 2", txt)
        self.assertIn("DIMENSIONAMENTO DO VENTILADOR", txt)
        self.assertIn("CONDUTO VERTICAL DE AR", txt)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_txt = gerar_csv_sanitizado(self.res)
        self.assertIn("sobrepressao_estagio1", csv_txt)
        self.assertIn("velocidade_escape_estagio2", csv_txt)
        self.assertIn("vazao_nominal_ventilador", csv_txt)

    def test_gerar_pacote_zip_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = os.path.join(tmpdir, "teste_pacote.zip")
            gerar_pacote_zip(self.res, caminho_zip, svg_conteudo="<svg></svg>")

            self.assertTrue(os.path.exists(caminho_zip))
            with zipfile.ZipFile(caminho_zip, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("memorial_descritivo.txt", nomes)
                self.assertIn("dados_dimensionamento.json", nomes)
                self.assertIn("resumo_dimensionamento.csv", nomes)
                self.assertIn("painel_esquematico.svg", nomes)

                # Verificar timestamp fixo determinístico 2026-01-01
                for info in zf.infolist():
                    self.assertEqual(info.date_time[:3], (2026, 1, 1))

            # Verificar que O_EXCL impede sobrescrita
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip(self.res, caminho_zip)


if __name__ == "__main__":
    unittest.main()
