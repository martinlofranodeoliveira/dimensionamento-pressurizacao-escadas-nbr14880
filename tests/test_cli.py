"""Testes da interface de linha de comando (CLI) da NBR 14880."""

import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from pressurizacao_nbr14880.cli import main


class TestCLI(unittest.TestCase):
    """Testa os comandos, flags e saídas da CLI pressurizacao-nbr14880."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.exemplo_json = os.path.join(self.tmpdir.name, "edificio_teste.json")
        with open(self.exemplo_json, "w", encoding="utf-8") as f:
            f.write("""{
                "nome_edificio": "Edifício Teste CLI",
                "quantidade_pavimentos": 12,
                "altura_total_m": "36.0",
                "tipo_escada": "enclausurada_protegida",
                "tipo_duto": "metalico_galvanizado",
                "possui_sprinklers": true,
                "quantidade_portas_simples": 12,
                "quantidade_portas_duplas": 0,
                "portas_abertas_projeto": 2,
                "perda_carga_distribuicao_pa": "250"
            }""")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_cli_sem_argumentos(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main([])
            self.assertEqual(code, 0)
            self.assertIn("pressurizacao-nbr14880", fake_out.getvalue())

    def test_cli_catalogo(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["catalogo"])
            self.assertEqual(code, 0)
            saida = fake_out.getvalue()
            self.assertIn("CATÁLOGO NORMATIVO", saida)
            self.assertIn("Diferencial de Pressão", saida)
            self.assertIn("MOTORES TRIFÁSICOS", saida)

    def test_cli_gerar_exemplo_stdout(self) -> None:
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            code = main(["gerar-exemplo"])
            self.assertEqual(code, 0)
            self.assertIn("nome_edificio", fake_out.getvalue())

    def test_cli_gerar_exemplo_arquivo(self) -> None:
        caminho_arq = os.path.join(self.tmpdir.name, "modelo.json")
        code = main(["gerar-exemplo", "--saida", caminho_arq])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(caminho_arq))

    def test_cli_calcular_arquivo_inexistente(self) -> None:
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            code = main(["calcular", "nao_existe.json"])
            self.assertEqual(code, 1)
            self.assertIn("Erro ao abrir", fake_err.getvalue())

    def test_cli_calcular_json_invalido(self) -> None:
        arq_inv = os.path.join(self.tmpdir.name, "invalido.json")
        with open(arq_inv, "w", encoding="utf-8") as f:
            f.write("{ quebrado json ")
        with patch("sys.stderr", new=io.StringIO()) as fake_err:
            code = main(["calcular", arq_inv])
            self.assertEqual(code, 1)
            self.assertIn("Erro de validação", fake_err.getvalue())

    def test_cli_calcular_formatos(self) -> None:
        for fmt in ["texto", "json", "csv", "svg"]:
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                code = main(["calcular", self.exemplo_json, "--formato", fmt])
                self.assertEqual(code, 0)
                conteudo = fake_out.getvalue()
                if fmt == "svg":
                    self.assertIn("<svg", conteudo)
                elif fmt == "json":
                    self.assertIn("ABNT NBR 14880:2014", conteudo)
                elif fmt == "csv":
                    self.assertIn("parametro;", conteudo)
                else:
                    self.assertIn("LOFRANO TECNOLOGIA", conteudo)

    def test_cli_calcular_saida_arquivo(self) -> None:
        saida_txt = os.path.join(self.tmpdir.name, "relatorio.txt")
        code = main(["calcular", self.exemplo_json, "--saida", saida_txt])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(saida_txt))

    def test_cli_calcular_pacote_zip(self) -> None:
        zip_path = os.path.join(self.tmpdir.name, "pacote.zip")
        code = main(["calcular", self.exemplo_json, "--pacote-zip", zip_path])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(zip_path))


if __name__ == "__main__":
    unittest.main()
