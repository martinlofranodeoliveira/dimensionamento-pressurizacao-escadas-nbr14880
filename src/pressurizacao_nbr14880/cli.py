"""Interface de linha de comando (CLI) para pressurização de escadas NBR 14880."""

import argparse
import sys
from fractions import Fraction
from typing import Optional

from pressurizacao_nbr14880.calculator import dimensionar_pressurizacao_escada
from pressurizacao_nbr14880.codecs import carregar_dados_edificacao_json, exportar_resultado_json
from pressurizacao_nbr14880.constants import (
    FORCA_MAXIMA_ABERTURA_PORTA_N,
    MOTORES_COMERCIAIS_CV,
    PRESSAO_DIFERENCIAL_MINIMA_PA,
    VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S,
    VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S,
    VELOCIDADE_MAX_DUTO_ALVENARIA_M_S,
    VELOCIDADE_MAX_DUTO_METALICO_M_S,
)
from pressurizacao_nbr14880.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip,
    gerar_relatorio_texto,
)
from pressurizacao_nbr14880.svg_generator import gerar_painel_svg

VERSAO = "1.0.0"


def cmd_calcular(args: argparse.Namespace) -> int:
    """Executa o cálculo de dimensionamento de pressurização da escada."""
    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except OSError as err:
        print(f"Erro ao abrir arquivo de projeto '{args.arquivo}': {err}", file=sys.stderr)
        return 1

    try:
        dados = carregar_dados_edificacao_json(conteudo)
    except ValueError as err:
        print(f"Erro de validação do arquivo JSON: {err}", file=sys.stderr)
        return 1

    resultado = dimensionar_pressurizacao_escada(dados)
    svg_conteudo = gerar_painel_svg(resultado)

    # Pacote determinístico ZIP
    if args.pacote_zip:
        try:
            gerar_pacote_zip(resultado, args.pacote_zip, svg_conteudo=svg_conteudo)
            print(f"[ZIP] Pacote determinístico gerado com sucesso em '{args.pacote_zip}'")
        except OSError as err:
            print(f"Erro ao gerar pacote ZIP '{args.pacote_zip}': {err}", file=sys.stderr)
            return 1

    # Formatação da saída
    formato = args.formato.lower()
    if formato == "json":
        saida_str = exportar_resultado_json(resultado)
    elif formato == "csv":
        saida_str = gerar_csv_sanitizado(resultado)
    elif formato == "svg":
        saida_str = svg_conteudo
    else:
        saida_str = gerar_relatorio_texto(resultado)

    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f_out:
                f_out.write(saida_str)
            print(f"[OK] Saída ({formato}) salva com sucesso em '{args.saida}'")
        except OSError as err:
            print(f"Erro ao gravar arquivo de saída '{args.saida}': {err}", file=sys.stderr)
            return 1
    else:
        print(saida_str)

    return 0


def cmd_catalogo(_args: argparse.Namespace) -> int:
    """Exibe os parâmetros normativos e catálogo de motores da NBR 14880:2014."""
    print("=" * 80)
    print("    CATÁLOGO NORMATIVO - ABNT NBR 14880:2014")
    print("=" * 80)
    print("1. CRITÉRIOS DE PRESSÃO E VELOCIDADE:")
    print(f"  • Diferencial de Pressão Mínimo (Portas Fechadas): {PRESSAO_DIFERENCIAL_MINIMA_PA} Pa")
    print(f"  • Força Máxima de Abertura da Porta:              {FORCA_MAXIMA_ABERTURA_PORTA_N} N")
    print(f"  • Velocidade de Escape (Com Sprinklers):           {VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S} m/s")
    print(f"  • Velocidade de Escape (Rota Crítica sem antec.):  {VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S} m/s")

    print("\n2. VELOCIDADES MÁXIMAS ADMISSÍVEIS EM DUTOS:")
    print(f"  • Dutos Metálicos Galvanizados:                    {VELOCIDADE_MAX_DUTO_METALICO_M_S} m/s")
    print(f"  • Dutos de Alvenaria ou Concreto:                  {VELOCIDADE_MAX_DUTO_ALVENARIA_M_S} m/s")

    print("\n3. MOTORES TRIFÁSICOS PADRONIZADOS (cv):")
    motores_str = ", ".join(f"{float(m):.1f} cv" for m in MOTORES_COMERCIAIS_CV)
    print(f"  • Linha comercial: {motores_str}")
    print("=" * 80)
    return 0


def cmd_gerar_exemplo(args: argparse.Namespace) -> int:
    """Gera um arquivo JSON de exemplo pronto para preenchimento."""
    exemplo_json = """{
  "nome_edificio": "Edifício Residencial Torre das Américas",
  "quantidade_pavimentos": 24,
  "altura_total_m": "72.0",
  "tipo_escada": "enclausurada_protegida",
  "tipo_duto": "metalico_galvanizado",
  "possui_sprinklers": true,
  "quantidade_portas_simples": 24,
  "quantidade_portas_duplas": 0,
  "portas_abertas_projeto": 2,
  "perda_carga_distribuicao_pa": "250"
}
"""
    if args.saida:
        try:
            with open(args.saida, "w", encoding="utf-8") as f:
                f.write(exemplo_json)
            print(f"[OK] Modelo de exemplo gravado em '{args.saida}'")
        except OSError as err:
            print(f"Erro ao salvar arquivo de exemplo '{args.saida}': {err}", file=sys.stderr)
            return 1
    else:
        print(exemplo_json)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = argparse.ArgumentParser(
        prog="pressurizacao-nbr14880",
        description="Dimensionamento de pressurização de escadas conforme ABNT NBR 14880:2014.",
    )
    parser.add_argument("--versao", action="version", version=f"%(prog)s {VERSAO}")
    parser.add_argument("--ajuda", action="help", help="Exibe esta mensagem de ajuda e encerra.")

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: calcular
    p_calc = subparsers.add_parser("calcular", help="Dimensionar projeto a partir de JSON")
    p_calc.add_argument("arquivo", help="Caminho do arquivo JSON com dados do edifício")
    p_calc.add_argument(
        "--formato",
        choices=["texto", "json", "csv", "svg"],
        default="texto",
        help="Formato de saída do memorial (padrão: texto)",
    )
    p_calc.add_argument("--saida", help="Caminho do arquivo para salvar o resultado")
    p_calc.add_argument("--pacote-zip", help="Gera pacote ZIP com memorial, JSON, CSV e SVG")

    # Comando: catalogo
    subparsers.add_parser("catalogo", help="Consultar parâmetros normativos e motores")

    # Comando: gerar-exemplo
    p_ex = subparsers.add_parser("gerar-exemplo", help="Gerar arquivo JSON de exemplo")
    p_ex.add_argument("--saida", help="Arquivo onde gravar o exemplo JSON")

    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "calcular":
        return cmd_calcular(args)
    if args.comando == "catalogo":
        return cmd_catalogo(args)
    if args.comando == "gerar-exemplo":
        return cmd_gerar_exemplo(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
