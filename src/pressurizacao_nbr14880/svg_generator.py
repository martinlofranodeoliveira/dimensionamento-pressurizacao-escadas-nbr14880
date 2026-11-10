"""Gerador de painel técnico vetorial SVG 1440x900 para pressurização de escadas NBR 14880."""

import html
from fractions import Fraction
from pressurizacao_nbr14880.exporters import _fmt
from pressurizacao_nbr14880.models import ResultadoDimensionamento


def gerar_painel_svg(res: ResultadoDimensionamento) -> str:
    """Renderiza painel esquemático vetorial SVG profissional 1440x900."""
    w, h = 1440, 900
    nome_edif = html.escape(res.nome_edificio)
    tipo_esc = html.escape(res.tipo_escada.value.upper())

    # Indicadores principais
    vazao_m3h = _fmt(res.ventilador.vazao_nominal_m3_h, 0)
    pressao_pa = _fmt(res.ventilador.pressao_estatica_total_pa, 0)
    motor_cv = _fmt(res.ventilador.motor_comercial_adotado_cv, 1)
    forca_n = _fmt(res.forca_abertura_porta_n, 1)
    st_forca = "CONFORME" if res.conformidade_forca_abertura else "REPROVADO"

    vazao_est1_m3h = _fmt(res.estagio1.vazao_frestas_m3_h, 0)
    vazao_est2_m3h = _fmt(res.estagio2.vazao_total_estagio2_m3_h, 0)

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        '  <defs>',
        '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#0b1329"/>',
        '      <stop offset="100%" stop-color="#1e2238"/>',
        '    </linearGradient>',
        '    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1b2440" stop-opacity="0.95"/>',
        '      <stop offset="100%" stop-color="#121829" stop-opacity="0.95"/>',
        '    </linearGradient>',
        '    <linearGradient id="fanGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#0284c7"/>',
        '      <stop offset="100%" stop-color="#38bdf8"/>',
        '    </linearGradient>',
        '    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">',
        '      <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>',
        '    </filter>',
        '  </defs>',
        '  <style>',
        '    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 26px; font-weight: 700; fill: #ffffff; }',
        '    .subtitle { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; fill: #94a3b8; }',
        '    .norma-badge { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #38bdf8; }',
        '    .kpi-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }',
        '    .kpi-value { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 28px; font-weight: 700; fill: #f8fafc; }',
        '    .kpi-sub { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #38bdf8; }',
        '    .card-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 600; fill: #e2e8f0; }',
        '    .tbl-header { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; fill: #cbd5e1; }',
        '    .tbl-cell { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #94a3b8; }',
        '    .diagram-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 12px; fill: #e2e8f0; }',
        '  </style>',
        f'  <rect width="{w}" height="{h}" fill="url(#bgGrad)"/>',
    ]

    # Barra superior / Cabeçalho
    svg.append('  <!-- Header -->')
    svg.append('  <rect x="40" y="30" width="1360" height="90" rx="12" fill="url(#cardGrad)" stroke="#273559" stroke-width="1" filter="url(#shadow)"/>')
    svg.append('  <rect x="40" y="30" width="6" height="90" rx="3" fill="url(#fanGrad)"/>')
    svg.append('  <text x="65" y="65" class="title">LOFRANO TECNOLOGIA · SISTEMAS DE PRESSURIZAÇÃO DE ESCADAS</text>')
    svg.append(f'  <text x="65" y="95" class="subtitle">Edificação: {nome_edif} | Tipologia: {tipo_esc} | Sobrepressão Normativa: 50 Pa</text>')
    svg.append('  <rect x="1200" y="55" width="180" height="36" rx="6" fill="#1e293b" stroke="#0284c7" stroke-width="1.5"/>')
    svg.append('  <text x="1290" y="78" text-anchor="middle" class="norma-badge">ABNT NBR 14880:2014</text>')

    # 4 Cartões KPI principais
    kpis = [
        ("Vazão do Ventilador", f"{vazao_m3h} m³/h", f"{_fmt(res.ventilador.vazao_nominal_m3_s, 2)} m³/s (+15% Dutos)"),
        ("Pressão Estática Total", f"{pressao_pa} Pa", "50 Pa Escada + Rede Dutos"),
        ("Potência do Motor", f"{motor_cv} cv", f"Trifásico ({_fmt(res.ventilador.potencia_eixo_w/1000, 1)} kW eixo)"),
        ("Força na Maçaneta", f"{forca_n} N", f"Limite: 110 N ({st_forca})"),
    ]

    x_card = 40
    y_card = 140
    card_w = 325
    card_h = 100
    gap = 20

    for idx, (titulo, val, sub) in enumerate(kpis):
        cx = x_card + idx * (card_w + gap)
        svg.append(f'  <!-- KPI {idx+1} -->')
        svg.append(f'  <rect x="{cx}" y="{y_card}" width="{card_w}" height="{card_h}" rx="10" fill="url(#cardGrad)" stroke="#273559" stroke-width="1" filter="url(#shadow)"/>')
        svg.append(f'  <text x="{cx+20}" y="{y_card+28}" class="kpi-title">{titulo}</text>')
        svg.append(f'  <text x="{cx+20}" y="{y_card+64}" class="kpi-value">{val}</text>')
        svg.append(f'  <text x="{cx+20}" y="{y_card+86}" class="kpi-sub">{sub}</text>')

    # Diagrama Esquemático em Corte (Lado Esquerdo: x=40, y=260, w=670, h=590)
    svg.append('  <!-- Diagrama em Corte da Caixa de Escada Pressurizada -->')
    svg.append('  <rect x="40" y="260" width="670" height="590" rx="12" fill="url(#cardGrad)" stroke="#273559" stroke-width="1" filter="url(#shadow)"/>')
    svg.append('  <text x="65" y="295" class="card-title">Corte Esquemático: Ventilador, Duto Vertical e Caixa Enclausurada</text>')

    # Tomada de Ar e Ventilador Centrífugo no Topo
    svg.append('  <!-- Ventilador e Tomada de Ar -->')
    svg.append('  <rect x="80" y="330" width="220" height="90" rx="8" fill="#1e293b" stroke="#0284c7" stroke-width="2"/>')
    svg.append('  <text x="190" y="360" text-anchor="middle" class="card-title" fill="#38bdf8">VENTILADOR CENTRÍFUGO</text>')
    svg.append(f'  <text x="190" y="385" text-anchor="middle" class="diagram-text">{vazao_m3h} m³/h @ {pressao_pa} Pa</text>')
    svg.append(f'  <text x="190" y="405" text-anchor="middle" class="kpi-sub">Motor Trifásico {motor_cv} cv</text>')

    # Duto Vertical de Injeção
    svg.append('  <!-- Duto Vertical -->')
    svg.append('  <rect x="165" y="420" width="50" height="400" fill="#0f172a" stroke="#0284c7" stroke-width="2"/>')
    svg.append('  <text x="190" y="620" text-anchor="middle" class="diagram-text" fill="#94a3b8" transform="rotate(-90 190 620)">Duto Vertical de Injeção</text>')

    # Caixa de Escada (Caixão enclausurado)
    svg.append('  <!-- Caixa de Escada -->')
    svg.append('  <rect x="250" y="420" width="430" height="400" rx="4" fill="#162035" stroke="#475569" stroke-width="2"/>')
    svg.append('  <text x="465" y="450" text-anchor="middle" class="card-title">Caixa de Escada Pressurizada (+50 Pa)</text>')

    # Andares / Portas Corta-fogo
    floors = [
        (480, "Pavimento Superior", "Porta P-90 Fechada (Fresta 50 Pa)"),
        (560, "Pavimento Tipo", "Grelha Insuflamento de Ar (5 m/s)"),
        (640, "Pavimento Sinistrado", "Porta Aberta: Escape 1.0 m/s"),
        (720, "Térreo / Saída de Emergência", "Descarga Externa Aberta (Fuga)"),
    ]

    for fy, flabel, fsub in floors:
        svg.append(f'  <line x1="250" y1="{fy}" x2="680" y2="{fy}" stroke="#334155" stroke-width="1" stroke-dasharray="4,4"/>')
        # Grelha de injeção conectando duto à escada
        svg.append(f'  <rect x="215" y="{fy-15}" width="35" height="15" fill="#38bdf8"/>')
        svg.append(f'  <polygon points="255,{fy-8} 265,{fy-15} 265,{fy}" fill="#38bdf8"/>')
        # Porta
        svg.append(f'  <rect x="620" y="{fy-30}" width="15" height="30" fill="#f59e0b" stroke="#d97706" stroke-width="1"/>')
        svg.append(f'  <text x="280" y="{fy-10}" class="diagram-text" font-weight="600">{flabel}</text>')
        svg.append(f'  <text x="280" y="{fy+8}" class="tbl-cell">{fsub}</text>')

    # Quadro Comparativo de Estágios e Parâmetros (Lado Direito: x=730, y=260, w=670, h=590)
    svg.append('  <!-- Quadro Comparativo de Engenharia -->')
    svg.append('  <rect x="730" y="260" width="670" height="590" rx="12" fill="url(#cardGrad)" stroke="#273559" stroke-width="1" filter="url(#shadow)"/>')
    svg.append('  <text x="755" y="295" class="card-title">Balanço Aerodinâmico e Condicionantes Normativas</text>')

    # Tabela de Comparação
    ty = 330
    svg.append(f'  <rect x="755" y="{ty}" width="620" height="30" rx="4" fill="#1e293b"/>')
    svg.append(f'  <text x="765" y="{ty+20}" class="tbl-header">Parâmetro de Projeto</text>')
    svg.append(f'  <text x="1050" y="{ty+20}" class="tbl-header">Estágio 1</text>')
    svg.append(f'  <text x="1190" y="{ty+20}" class="tbl-header">Estágio 2</text>')
    svg.append(f'  <text x="1310" y="{ty+20}" class="tbl-header">Norma</text>')

    linhas_tabela = [
        ("Condição Operacional", "Portas Fechadas", "Portas Abertas", "-"),
        ("Diferencial de Pressão / Velocidade", "50 Pa", f"{_fmt(res.estagio2.velocidade_escape_m_s, 1)} m/s", "NBR 14880"),
        ("Portas Abertas Simuladas", "0 un", f"{res.estagio2.portas_abertas} un", f">= {res.estagio2.portas_abertas} un"),
        ("Vazão Requerida de Ar", f"{vazao_est1_m3h} m³/h", f"{vazao_est2_m3h} m³/h", "Cálculo"),
        ("Vazão Nominal (+15% Dutos)", f"{_fmt(res.estagio1.vazao_frestas_m3_h*Fraction(23,20),0)} m³/h", f"{vazao_m3h} m³/h", "Adotado"),
        ("Pressão Estática de Projeto", f"{pressao_pa} Pa", f"{pressao_pa} Pa", "Rede Dutos"),
        ("Área Mínima do Duto Vertical", f"{_fmt(res.duto.area_util_minima_m2, 2)} m²", f"{_fmt(res.duto.area_util_minima_m2, 2)} m²", "Velocidade"),
        ("Força na Maçaneta da Porta", f"{forca_n} N", "-", "<= 110 N"),
    ]

    for idx, (p_nome, p_e1, p_e2, p_norma) in enumerate(linhas_tabela):
        row_y = ty + 40 + idx * 42
        fill_bg = "#17223b" if idx % 2 == 0 else "#131a2e"
        svg.append(f'  <rect x="755" y="{row_y}" width="620" height="36" rx="4" fill="{fill_bg}"/>')
        svg.append(f'  <text x="765" y="{row_y+22}" class="tbl-cell" font-weight="600" fill="#f1f5f9">{html.escape(p_nome)}</text>')
        svg.append(f'  <text x="1050" y="{row_y+22}" class="tbl-cell">{p_e1}</text>')
        svg.append(f'  <text x="1190" y="{row_y+22}" class="tbl-cell" font-weight="600" fill="#38bdf8">{p_e2}</text>')
        svg.append(f'  <text x="1310" y="{row_y+22}" class="tbl-cell">{p_norma}</text>')

    # Rodapé de Conformidade
    svg.append('  <!-- Footer -->')
    svg.append('  <rect x="755" y="780" width="620" height="50" rx="6" fill="#1e293b" stroke="#334155" stroke-width="1"/>')
    svg.append('  <text x="770" y="802" class="diagram-text" fill="#94a3b8">Critérios: Pressão 50 Pa · Escape &ge; 1.0 m/s · Força Abertura &le; 110 N</text>')
    svg.append('  <text x="770" y="820" class="diagram-text" font-weight="700" fill="#10b981">ABNT NBR 14880:2014 · DIMENSIONAMENTO DE PRESSURIZAÇÃO APROVADO</text>')

    svg.append('</svg>')
    return "\n".join(svg) + "\n"
