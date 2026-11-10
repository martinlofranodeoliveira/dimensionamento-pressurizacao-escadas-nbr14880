"""Exportadores técnicos: memorial descritivo, CSV sanitizado e ZIP determinístico."""

import csv
import io
import os
import zipfile
from fractions import Fraction
from typing import Optional

from pressurizacao_nbr14880.codecs import exportar_resultado_json
from pressurizacao_nbr14880.models import ResultadoDimensionamento


def _fmt(val: Fraction, casas: int = 2) -> str:
    """Formata fração para string decimal com número fixo de casas sem IEEE float."""
    num = val.numerator
    den = val.denominator
    if den == 1:
        return f"{num}.0" if casas > 0 else str(num)
    inteiro = num // den
    resto = abs(num % den)
    fator = 10**casas
    frac_parte = (resto * fator + den // 2) // den
    return f"{inteiro}.{frac_parte:0{casas}d}"


def _sanitizar_campo_csv(val: str) -> str:
    """Sanitiza strings contra injeção de fórmulas de planilhas."""
    if val and val[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{val}"
    return val


def gerar_relatorio_texto(res: ResultadoDimensionamento) -> str:
    """Gera memorial descritivo técnico detalhado de pressurização de escadas."""
    linhas: list[str] = []
    w = 80
    linhas.append("=" * w)
    linhas.append("    LOFRANO TECNOLOGIA - ENGENHARIA DE SEGURANÇA CONTRA INCÊNDIO")
    linhas.append("    PRESSURIZAÇÃO DE ESCADAS DE SEGURANÇA - ABNT NBR 14880:2014")
    linhas.append("=" * w)
    linhas.append(f"Edificação: {res.nome_edificio}")
    linhas.append(f"Tipologia:  {res.tipo_escada.value.upper()}")
    linhas.append("-" * w)

    linhas.append("1. ESTÁGIO 1 - PORTAS FECHADAS (SOBREPRESSÃO 50 Pa)")
    linhas.append(f"  - Diferencial de Pressão Regulamentar:   {_fmt(res.estagio1.pressao_diferencial_pa, 0)} Pa")
    linhas.append(f"  - Área Total de Frestas Perimetrais:     {_fmt(res.estagio1.area_total_frestas_m2, 4)} m²")
    linhas.append(f"  - Vazão de Vazamento por Frestas:        {_fmt(res.estagio1.vazao_frestas_m3_s, 3)} m³/s ({_fmt(res.estagio1.vazao_frestas_m3_h, 0)} m³/h)")
    linhas.append("-" * w)

    linhas.append("2. ESTÁGIO 2 - PORTAS ABERTAS (VELOCIDADE DE ESCAPE)")
    linhas.append(f"  - Velocidade Mínima de Escape de Ar:     {_fmt(res.estagio2.velocidade_escape_m_s, 2)} m/s")
    linhas.append(f"  - Quantidade de Portas Abertas Simuladas:{res.estagio2.portas_abertas} porta(s)")
    linhas.append(f"  - Área Total de Passagem Livre Aberta:   {_fmt(res.estagio2.area_abertura_total_m2, 2)} m²")
    linhas.append(f"  - Vazão de Escape nas Portas Abertas:    {_fmt(res.estagio2.vazao_portas_abertas_m3_s, 3)} m³/s")
    linhas.append(f"  - Vazão Residual nas Portas Fechadas:    {_fmt(res.estagio2.vazao_portas_fechadas_m3_s, 3)} m³/s")
    linhas.append(f"  - Vazão Total Requerida no Estágio 2:    {_fmt(res.estagio2.vazao_total_estagio2_m3_s, 3)} m³/s ({_fmt(res.estagio2.vazao_total_estagio2_m3_h, 0)} m³/h)")
    linhas.append("-" * w)

    linhas.append("3. DIMENSIONAMENTO DO VENTILADOR CENTRÍFUGO DE PRESSURIZAÇÃO")
    linhas.append(f"  - Vazão Nominal de Projeto (+15% duto):  {_fmt(res.ventilador.vazao_nominal_m3_s, 3)} m³/s ({_fmt(res.ventilador.vazao_nominal_m3_h, 0)} m³/h)")
    linhas.append(f"  - Pressão Estática Total do Sistema:     {_fmt(res.ventilador.pressao_estatica_total_pa, 0)} Pa")
    linhas.append(f"  - Rendimento Aerodinâmico Adotado:       {_fmt(res.ventilador.rendimento_aerodinamico * Fraction(100, 1), 0)}%")
    linhas.append(f"  - Potência no Eixo do Ventilador:        {_fmt(res.ventilador.potencia_eixo_w, 1)} W")
    linhas.append(f"  - Potência do Motor Elétrico (+15% mar): {_fmt(res.ventilador.potencia_motor_calculada_cv, 2)} cv")
    linhas.append(f"  - MOTOR COMERCIAL TRIFÁSICO ADOTADO:     {_fmt(res.ventilador.motor_comercial_adotado_cv, 1)} cv")
    linhas.append("-" * w)

    linhas.append("4. CONDUTO VERTICAL DE AR (DUTO DE INJEÇÃO)")
    linhas.append(f"  - Material / Tipologia do Duto:          {res.duto.tipo_duto.value}")
    linhas.append(f"  - Velocidade Adotada no Duto:            {_fmt(res.duto.velocidade_adotada_m_s, 1)} m/s (Máx: {_fmt(res.duto.velocidade_maxima_permitida_m_s, 1)} m/s)")
    linhas.append(f"  - Área Útil Mínima de Seção do Duto:     {_fmt(res.duto.area_util_minima_m2, 3)} m²")
    linhas.append(f"  - Dimensão Sugerida do Duto:             {res.duto.dimensao_sugerida}")
    linhas.append("-" * w)

    st_forca = "CONFORME" if res.conformidade_forca_abertura else "REPROVADO"
    linhas.append("5. FORÇA MÁXIMA DE ABERTURA DA PORTA (NBR 14880, ITEM 5.1.3)")
    linhas.append(f"  - Força Máxima Calculada na Maçaneta:    {_fmt(res.forca_abertura_porta_n, 1)} N [{st_forca}]")
    linhas.append(f"  - Limite Máximo Regulamentar:            110,0 N (Segurança e Ergonomia de Evacuação)")
    linhas.append("-" * w)

    linhas.append("6. RECOMENDAÇÕES E DIRETRIZES TÉCNICAS")
    for rec in res.recomendacoes:
        linhas.append(f"  * {rec}")
    if res.alertas:
        linhas.append("-" * w)
        linhas.append("7. ALERTAS DE PROJETO")
        for alt in res.alertas:
            linhas.append(f"  ! {alt}")

    linhas.append("=" * w)
    linhas.append("Emitido via Lofrano Tecnologia - Conforme ABNT NBR 14880:2014")
    linhas.append("=" * w)
    return "\n".join(linhas) + "\n"


def gerar_csv_sanitizado(res: ResultadoDimensionamento) -> str:
    """Gera resumo tabular CSV protegido contra fórmula injection."""
    saida = io.StringIO()
    writer = csv.writer(saida, delimiter=";", lineterminator="\n")

    writer.writerow([
        _sanitizar_campo_csv("parametro"),
        _sanitizar_campo_csv("unidade"),
        _sanitizar_campo_csv("valor"),
        _sanitizar_campo_csv("limite_normativo"),
        _sanitizar_campo_csv("status"),
    ])

    writer.writerow([
        _sanitizar_campo_csv("sobrepressao_estagio1"),
        "Pa",
        _fmt(res.estagio1.pressao_diferencial_pa, 0),
        "50 Pa",
        "CONFORME",
    ])
    writer.writerow([
        _sanitizar_campo_csv("vazao_estagio1"),
        "m3/h",
        _fmt(res.estagio1.vazao_frestas_m3_h, 0),
        "-",
        "INFO",
    ])
    writer.writerow([
        _sanitizar_campo_csv("velocidade_escape_estagio2"),
        "m/s",
        _fmt(res.estagio2.velocidade_escape_m_s, 2),
        ">= 1.0 m/s",
        "CONFORME",
    ])
    writer.writerow([
        _sanitizar_campo_csv("vazao_estagio2"),
        "m3/h",
        _fmt(res.estagio2.vazao_total_estagio2_m3_h, 0),
        "-",
        "INFO",
    ])
    writer.writerow([
        _sanitizar_campo_csv("vazao_nominal_ventilador"),
        "m3/h",
        _fmt(res.ventilador.vazao_nominal_m3_h, 0),
        "-",
        "DIMENSIONADO",
    ])
    writer.writerow([
        _sanitizar_campo_csv("motor_ventilador"),
        "cv",
        _fmt(res.ventilador.motor_comercial_adotado_cv, 1),
        "-",
        "COMERCIAL",
    ])
    writer.writerow([
        _sanitizar_campo_csv("area_util_duto"),
        "m2",
        _fmt(res.duto.area_util_minima_m2, 3),
        "-",
        "DIMENSIONADO",
    ])
    writer.writerow([
        _sanitizar_campo_csv("forca_abertura_porta"),
        "N",
        _fmt(res.forca_abertura_porta_n, 1),
        "<= 110 N",
        "CONFORME" if res.conformidade_forca_abertura else "REPROVADO",
    ])

    return saida.getvalue()


def gerar_pacote_zip(res: ResultadoDimensionamento, caminho_zip: str, svg_conteudo: Optional[str] = None) -> None:
    """Gera pacote determinístico ZIP com O_EXCL, evitando sobrescrita acidental."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    fd = os.open(caminho_zip, flags, 0o644)
    fixed_time = (2026, 1, 1, 0, 0, 0)

    try:
        with open(fd, "wb", closefd=True) as f_out:
            with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # 1. Memorial descritivo em texto
                txt = gerar_relatorio_texto(res).encode("utf-8")
                zi_txt = zipfile.ZipInfo(filename="memorial_descritivo.txt", date_time=fixed_time)
                zf.writestr(zi_txt, txt)

                # 2. Dados em JSON canônico
                js = exportar_resultado_json(res).encode("utf-8")
                zi_js = zipfile.ZipInfo(filename="dados_dimensionamento.json", date_time=fixed_time)
                zf.writestr(zi_js, js)

                # 3. Planilha CSV sanitizada
                csv_data = gerar_csv_sanitizado(res).encode("utf-8")
                zi_csv = zipfile.ZipInfo(filename="resumo_dimensionamento.csv", date_time=fixed_time)
                zf.writestr(zi_csv, csv_data)

                # 4. Painel vetorial SVG se disponível
                if svg_conteudo:
                    svg_bytes = svg_conteudo.encode("utf-8")
                    zi_svg = zipfile.ZipInfo(filename="painel_esquematico.svg", date_time=fixed_time)
                    zf.writestr(zi_svg, svg_bytes)
    except Exception:
        if os.path.exists(caminho_zip):
            try:
                os.remove(caminho_zip)
            except OSError:
                pass
        raise
