"""Testes avançados, casos de borda e validações rigorosas para NBR 14880."""

import os
import tempfile
import unittest
from fractions import Fraction

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.constants import (
    AREA_FRESTA_PORTA_DUPLA_M2,
    AREA_FRESTA_PORTA_SIMPLES_M2,
    COEFICIENTE_VAZAMENTO_FRESTA_50PA,
    CONVERSAO_WATT_PARA_CV,
    FATOR_MAJORACAO_VAZAMENTOS_DUTO,
    LARGURA_PORTA_PADRAO_M,
    MARGEM_SEGURANCA_MOTOR,
    PRESSAO_DIFERENCIAL_MINIMA_PA,
    VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S,
    VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S,
)
from pressurizacao_nbr14880.exporters import gerar_csv_sanitizado, gerar_pacote_zip, gerar_relatorio_texto
from pressurizacao_nbr14880.models import DadosEdificacao, TipoDuto, TipoEscada


class TestCasosAvancados(unittest.TestCase):
    """Bateria de testes complementares de conformidade com a NBR 14880."""

    def setUp(self) -> None:
        self.dados_base = DadosEdificacao(
            nome_edificio="Torre Teste Avançado",
            quantidade_pavimentos=15,
            altura_total_m=Fraction(45, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=14,
            quantidade_portas_duplas=2,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(220, 1),
        )

    def test_calculo_exato_area_frestas_mistas(self) -> None:
        """Verifica a soma exata de frestas de portas simples e duplas."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        area_esperada = (14 * AREA_FRESTA_PORTA_SIMPLES_M2) + (2 * AREA_FRESTA_PORTA_DUPLA_M2)
        self.assertEqual(res.estagio1.area_total_frestas_m2, area_esperada)
        vazao_esperada = area_esperada * COEFICIENTE_VAZAMENTO_FRESTA_50PA
        self.assertEqual(res.estagio1.vazao_frestas_m3_s, vazao_esperada)

    def test_relacao_exata_m3_s_para_m3_h(self) -> None:
        """Garante que a vazão em m³/h é rigorosamente 3600 vezes a vazão em m³/s."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        self.assertEqual(res.estagio1.vazao_frestas_m3_h, res.estagio1.vazao_frestas_m3_s * 3600)
        self.assertEqual(res.estagio2.vazao_total_estagio2_m3_h, res.estagio2.vazao_total_estagio2_m3_s * 3600)
        self.assertEqual(res.ventilador.vazao_nominal_m3_h, res.ventilador.vazao_nominal_m3_s * 3600)

    def test_majoracao_duto_quinze_por_cento(self) -> None:
        """Valida que a vazão de projeto inclui o fator regulamentar de 15% (23/20)."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        maior_vazao = max(res.estagio1.vazao_frestas_m3_s, res.estagio2.vazao_total_estagio2_m3_s)
        self.assertEqual(res.ventilador.vazao_nominal_m3_s, maior_vazao * FATOR_MAJORACAO_VAZAMENTOS_DUTO)

    def test_potencia_aerodinamica_e_eletrica(self) -> None:
        """Valida as formulações de potência de eixo e de motor trifásico sem float."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        p_eixo_esperada = (res.ventilador.vazao_nominal_m3_s * res.ventilador.pressao_estatica_total_pa) / res.ventilador.rendimento_aerodinamico
        self.assertEqual(res.ventilador.potencia_eixo_w, p_eixo_esperada)

        potencia_motor_esperada_cv = p_eixo_esperada * MARGEM_SEGURANCA_MOTOR * CONVERSAO_WATT_PARA_CV
        self.assertEqual(res.ventilador.potencia_motor_calculada_cv, potencia_motor_esperada_cv)

    def test_area_util_duto_formula_continuidade(self) -> None:
        """A = Q / v conforme a equação da continuidade."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        area_duto_esperada = res.ventilador.vazao_nominal_m3_s / res.duto.velocidade_adotada_m_s
        self.assertEqual(res.duto.area_util_minima_m2, area_duto_esperada)

    def test_validacao_campos_invalidos_edificacao(self) -> None:
        """Testa exceções ao instanciar DadosEdificacao com valores nulos ou negativos."""
        with self.assertRaises(ValueError):
            DadosEdificacao(
                nome_edificio="",
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

        with self.assertRaises(ValueError):
            DadosEdificacao(
                nome_edificio="Edifício Zero Pavimentos",
                quantidade_pavimentos=0,
                altura_total_m=Fraction(30, 1),
                tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
                tipo_duto=TipoDuto.METALICO_GALVANIZADO,
                possui_sprinklers=True,
                quantidade_portas_simples=10,
                quantidade_portas_duplas=0,
                portas_abertas_projeto=1,
                perda_carga_distribuicao_pa=Fraction(200, 1),
            )

        with self.assertRaises(ValueError):
            DadosEdificacao(
                nome_edificio="Edifício Sem Portas",
                quantidade_pavimentos=5,
                altura_total_m=Fraction(15, 1),
                tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
                tipo_duto=TipoDuto.METALICO_GALVANIZADO,
                possui_sprinklers=True,
                quantidade_portas_simples=0,
                quantidade_portas_duplas=0,
                portas_abertas_projeto=1,
                perda_carga_distribuicao_pa=Fraction(200, 1),
            )

    def test_comparacao_rota_critica_sem_sprinklers(self) -> None:
        """Testa que a escada direta sem sprinklers exige velocidade de 2.0 m/s e maior vazão."""
        dados_com_sprinklers = DadosEdificacao(
            nome_edificio="Com Sprinklers",
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
        dados_sem_sprinklers = DadosEdificacao(
            nome_edificio="Sem Sprinklers Rota Crítica",
            quantidade_pavimentos=8,
            altura_total_m=Fraction(24, 1),
            tipo_escada=TipoEscada.PRESSURIZADA_DIRETA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=False,
            quantidade_portas_simples=8,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(200, 1),
        )
        res_com = dimensionar_pressurizacao_escada(dados_com_sprinklers)
        res_sem = dimensionar_pressurizacao_escada(dados_sem_sprinklers)

        self.assertEqual(res_com.estagio2.velocidade_escape_m_s, VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S)
        self.assertEqual(res_sem.estagio2.velocidade_escape_m_s, VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S)
        self.assertGreater(res_sem.ventilador.vazao_nominal_m3_s, res_com.ventilador.vazao_nominal_m3_s)

    def test_pressao_distribuicao_elevada(self) -> None:
        """Testa o comportamento com perda de carga estática de 450 Pa."""
        dados_alta_pressao = DadosEdificacao(
            nome_edificio="Prédio Duto Estreito",
            quantidade_pavimentos=10,
            altura_total_m=Fraction(30, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=10,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(450, 1),
        )
        res = dimensionar_pressurizacao_escada(dados_alta_pressao)
        self.assertEqual(res.ventilador.pressao_estatica_total_pa, Fraction(500, 1))

    def test_dimensao_sugerida_duto_alvenaria(self) -> None:
        """Verifica velocidade adotada e dimensão do duto em alvenaria."""
        dados_alv = DadosEdificacao(
            nome_edificio="Torre Concreto",
            quantidade_pavimentos=12,
            altura_total_m=Fraction(36, 1),
            tipo_escada=TipoEscada.ENCLAUSURADA_PROTEGIDA,
            tipo_duto=TipoDuto.ALVENARIA_CONCRETO,
            possui_sprinklers=True,
            quantidade_portas_simples=12,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=2,
            perda_carga_distribuicao_pa=Fraction(250, 1),
        )
        res = dimensionar_pressurizacao_escada(dados_alv)
        self.assertEqual(res.duto.velocidade_adotada_m_s, Fraction(8, 1))
        self.assertIn("1m x", res.duto.dimensao_sugerida)

    def test_alerta_emissao_portas_abertas_ajustadas(self) -> None:
        """Valida a emissão de alerta técnico quando portas abertas < mínimo normativo."""
        dados_edificio_alto = DadosEdificacao(
            nome_edificio="Edifício Comercial 25 Andares",
            quantidade_pavimentos=25,
            altura_total_m=Fraction(75, 1),
            tipo_escada=TipoEscada.COM_ANTECAMARA,
            tipo_duto=TipoDuto.METALICO_GALVANIZADO,
            possui_sprinklers=True,
            quantidade_portas_simples=25,
            quantidade_portas_duplas=0,
            portas_abertas_projeto=1,
            perda_carga_distribuicao_pa=Fraction(300, 1),
        )
        res = dimensionar_pressurizacao_escada(dados_edificio_alto)
        self.assertEqual(res.estagio2.portas_abertas, 2)
        self.assertTrue(len(res.alertas) > 0)
        self.assertTrue(any("exige no mínimo 2 portas abertas" in a for a in res.alertas))

    def test_exportacao_csv_sanitizado(self) -> None:
        """Testa se a exportação CSV contém os cabeçalhos esperados e linhas corretas."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        csv_texto = gerar_csv_sanitizado(res)
        self.assertIn("parametro;unidade;valor;limite_normativo;status", csv_texto)
        self.assertIn("sobrepressao_estagio1", csv_texto)
        self.assertIn("vazao_nominal_ventilador", csv_texto)
        self.assertIn("forca_abertura_porta", csv_texto)

    def test_relatorio_texto_formatacao(self) -> None:
        """Verifica se o relatório em texto inclui as seções numeradas."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        relatorio = gerar_relatorio_texto(res)
        self.assertIn("1. ESTÁGIO 1 - PORTAS FECHADAS", relatorio)
        self.assertIn("2. ESTÁGIO 2 - PORTAS ABERTAS", relatorio)
        self.assertIn("3. DIMENSIONAMENTO DO VENTILADOR CENTRÍFUGO", relatorio)
        self.assertIn("4. CONDUTO VERTICAL DE AR (DUTO DE INJEÇÃO)", relatorio)
        self.assertIn("5. FORÇA MÁXIMA DE ABERTURA DA PORTA", relatorio)
        self.assertIn("6. RECOMENDAÇÕES E DIRETRIZES TÉCNICAS", relatorio)

    def test_exportar_pacote_zip_com_bloqueio_sobrescrita(self) -> None:
        """Valida que o pacote ZIP determinístico rejeita sobrescrever arquivo existente."""
        res = dimensionar_pressurizacao_escada(self.dados_base)
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho_zip = os.path.join(tmpdir, "pacote_teste.zip")
            # Primeira criação: sucesso
            gerar_pacote_zip(res, caminho_zip)
            self.assertTrue(os.path.exists(caminho_zip))
            # Segunda criação: deve levantar FileExistsError devido a O_EXCL
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip(res, caminho_zip)


if __name__ == "__main__":
    unittest.main()
