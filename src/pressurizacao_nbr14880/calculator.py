"""Motor de cálculo aerodinâmico e termodinâmico da ABNT NBR 14880:2014."""

from fractions import Fraction
from pressurizacao_nbr14880.constants import (
    AREA_FRESTA_PORTA_DUPLA_M2,
    AREA_FRESTA_PORTA_SIMPLES_M2,
    AREA_PASSAGEM_PORTA_PADRAO_M2,
    COEFICIENTE_VAZAMENTO_FRESTA_50PA,
    CONVERSAO_WATT_PARA_CV,
    FATOR_MAJORACAO_VAZAMENTOS_DUTO,
    FORCA_MAXIMA_ABERTURA_PORTA_N,
    LARGURA_PORTA_PADRAO_M,
    MARGEM_SEGURANCA_MOTOR,
    MOTORES_COMERCIAIS_CV,
    PRESSAO_DIFERENCIAL_MAXIMA_PA,
    PRESSAO_DIFERENCIAL_MINIMA_PA,
    RENDIMENTO_PADRAO_VENTILADOR,
    VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S,
    VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S,
    VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S,
    VELOCIDADE_MAX_DUTO_ALVENARIA_M_S,
    VELOCIDADE_MAX_DUTO_METALICO_M_S,
)
from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    ResultadoDimensionamento,
    ResultadoDuto,
    ResultadoEstagio1,
    ResultadoEstagio2,
    ResultadoVentilador,
    TipoDuto,
    TipoEscada,
)


def _teto_fracao(frac: Fraction) -> int:
    """Calcula o teto inteiro exato de uma fração sem utilizar float."""
    if frac.denominator == 1:
        return frac.numerator
    if frac.numerator > 0:
        return (frac.numerator // frac.denominator) + 1
    return frac.numerator // frac.denominator


def dimensionar_pressurizacao_escada(dados: DadosEdificacao) -> ResultadoDimensionamento:
    """Executa o dimensionamento completo dos Estágios 1 e 2 da NBR 14880:2014."""
    alertas: list[str] = []
    recomendacoes: list[str] = []

    # 1. Determinação normativa do número de portas abertas
    minimo_portas_abertas = 1
    if dados.quantidade_pavimentos > 10 or dados.altura_total_m > Fraction(30, 1):
        minimo_portas_abertas = 2

    portas_abertas = dados.portas_abertas_projeto
    if portas_abertas < minimo_portas_abertas:
        alertas.append(
            f"Edificação com {dados.quantidade_pavimentos} pavimentos ({dados.altura_total_m}m) exige no mínimo {minimo_portas_abertas} portas abertas de projeto. Ajustado para {minimo_portas_abertas}."
        )
        portas_abertas = minimo_portas_abertas

    # 2. ESTÁGIO 1 - Portas Fechadas (Sobrepressão de 50 Pa)
    area_frestas_simples = Fraction(dados.quantidade_portas_simples, 1) * AREA_FRESTA_PORTA_SIMPLES_M2
    area_frestas_duplas = Fraction(dados.quantidade_portas_duplas, 1) * AREA_FRESTA_PORTA_DUPLA_M2
    area_total_frestas = area_frestas_simples + area_frestas_duplas

    vazao_frestas_m3_s = area_total_frestas * COEFICIENTE_VAZAMENTO_FRESTA_50PA
    vazao_frestas_m3_h = vazao_frestas_m3_s * Fraction(3600, 1)

    res_estagio1 = ResultadoEstagio1(
        pressao_diferencial_pa=PRESSAO_DIFERENCIAL_MINIMA_PA,
        area_total_frestas_m2=area_total_frestas,
        vazao_frestas_m3_s=vazao_frestas_m3_s,
        vazao_frestas_m3_h=vazao_frestas_m3_h,
    )

    # 3. ESTÁGIO 2 - Portas Abertas (Velocidade de Escape)
    if dados.tipo_escada == TipoEscada.PRESSURIZADA_DIRETA and not dados.possui_sprinklers:
        v_escape = VELOCIDADE_ESCAPE_ROTA_CRITICA_M_S  # 2.0 m/s
    elif dados.possui_sprinklers:
        v_escape = VELOCIDADE_ESCAPE_COM_SPRINKLERS_M_S  # 1.0 m/s
    else:
        v_escape = VELOCIDADE_ESCAPE_SEM_SPRINKLERS_M_S  # 1.0 m/s

    area_portas_abertas = Fraction(portas_abertas, 1) * AREA_PASSAGEM_PORTA_PADRAO_M2
    vazao_portas_abertas_m3_s = area_portas_abertas * v_escape

    # Frestas remanescentes de portas fechadas
    portas_simples_fechadas = max(0, dados.quantidade_portas_simples - portas_abertas)
    area_frestas_remanescentes = (
        Fraction(portas_simples_fechadas, 1) * AREA_FRESTA_PORTA_SIMPLES_M2
        + area_frestas_duplas
    )
    # No estágio 2, o diferencial médio residual nas portas fechadas reduz a vazão
    vazao_frestas_estagio2 = area_frestas_remanescentes * (COEFICIENTE_VAZAMENTO_FRESTA_50PA / Fraction(2, 1))

    vazao_total_estagio2_m3_s = vazao_portas_abertas_m3_s + vazao_frestas_estagio2
    vazao_total_estagio2_m3_h = vazao_total_estagio2_m3_s * Fraction(3600, 1)

    res_estagio2 = ResultadoEstagio2(
        velocidade_escape_m_s=v_escape,
        portas_abertas=portas_abertas,
        area_abertura_total_m2=area_portas_abertas,
        vazao_portas_abertas_m3_s=vazao_portas_abertas_m3_s,
        vazao_portas_fechadas_m3_s=vazao_frestas_estagio2,
        vazao_total_estagio2_m3_s=vazao_total_estagio2_m3_s,
        vazao_total_estagio2_m3_h=vazao_total_estagio2_m3_h,
    )

    # 4. DIMENSIONAMENTO DO VENTILADOR
    # Maior vazão entre Estágio 1 e 2 com majoração de 15% por vazamento em dutos
    vazao_base = max(vazao_frestas_m3_s, vazao_total_estagio2_m3_s)
    vazao_nominal_m3_s = vazao_base * FATOR_MAJORACAO_VAZAMENTOS_DUTO
    vazao_nominal_m3_h = vazao_nominal_m3_s * Fraction(3600, 1)

    # Perda de carga total
    perda_dist = dados.perda_carga_distribuicao_pa if dados.perda_carga_distribuicao_pa > 0 else Fraction(200, 1)
    pressao_estatica_total = PRESSAO_DIFERENCIAL_MINIMA_PA + perda_dist

    # Potência eletromecânica
    pot_eixo_w = (vazao_nominal_m3_s * pressao_estatica_total) / RENDIMENTO_PADRAO_VENTILADOR
    pot_motor_w = pot_eixo_w * MARGEM_SEGURANCA_MOTOR
    pot_motor_cv = pot_motor_w * CONVERSAO_WATT_PARA_CV

    # Seleção de motor comercial
    motor_adotado_cv = MOTORES_COMERCIAIS_CV[-1]
    for m in MOTORES_COMERCIAIS_CV:
        if m >= pot_motor_cv:
            motor_adotado_cv = m
            break

    res_ventilador = ResultadoVentilador(
        vazao_nominal_m3_s=vazao_nominal_m3_s,
        vazao_nominal_m3_h=vazao_nominal_m3_h,
        pressao_estatica_total_pa=pressao_estatica_total,
        rendimento_aerodinamico=RENDIMENTO_PADRAO_VENTILADOR,
        potencia_eixo_w=pot_eixo_w,
        potencia_motor_calculada_cv=pot_motor_cv,
        motor_comercial_adotado_cv=motor_adotado_cv,
    )

    # 5. DIMENSIONAMENTO DO DUTO VERTICAL
    if dados.tipo_duto == TipoDuto.METALICO_GALVANIZADO:
        v_max_duto = VELOCIDADE_MAX_DUTO_METALICO_M_S
        v_adotada = Fraction(12, 1)  # 12 m/s
    else:
        v_max_duto = VELOCIDADE_MAX_DUTO_ALVENARIA_M_S
        v_adotada = Fraction(8, 1)  # 8 m/s

    area_duto_m2 = vazao_nominal_m3_s / v_adotada
    # Dimensão sugerida retangular aproximada (largura x profundidade)
    largura_m = Fraction(1, 1)
    profundidade_m = area_duto_m2 / largura_m
    dimensao_txt = f"{largura_m}m x {profundidade_m}m"

    res_duto = ResultadoDuto(
        tipo_duto=dados.tipo_duto,
        velocidade_maxima_permitida_m_s=v_max_duto,
        velocidade_adotada_m_s=v_adotada,
        area_util_minima_m2=area_duto_m2,
        dimensao_sugerida=dimensao_txt,
    )

    # 6. FORÇA DE ABERTURA DA PORTA CORTA-FOGO (Item 5.1.3)
    # F = F_mola + (A_porta * DeltaP) / 2
    forca_mola_n = Fraction(35, 1)
    forca_pressao_n = (AREA_PASSAGEM_PORTA_PADRAO_M2 * PRESSAO_DIFERENCIAL_MINIMA_PA) / Fraction(2, 1)
    forca_abertura_total_n = forca_mola_n + forca_pressao_n
    conforme_forca = forca_abertura_total_n <= FORCA_MAXIMA_ABERTURA_PORTA_N

    if not conforme_forca:
        alertas.append(
            f"Força de abertura da porta ({forca_abertura_total_n} N) excede o limite normativo de 110 N. Risco de retenção de ocupantes na evacuação."
        )

    # 7. RECOMENDAÇÕES NORMATIVAS
    recomendacoes.append(
        f"Sistema dimensionado sob tipologia '{dados.tipo_escada.value}' conforme ABNT NBR 14880:2014."
    )
    recomendacoes.append(
        f"Estágio 1 (portas fechadas): diferencial de pressão regulamentar de {PRESSAO_DIFERENCIAL_MINIMA_PA} Pa garantido."
    )
    recomendacoes.append(
        f"Estágio 2 (portas abertas): velocidade mínima de escape de {v_escape} m/s com {portas_abertas} porta(s) aberta(s)."
    )
    recomendacoes.append(
        f"Duto de injeção '{dados.tipo_duto.value}' dimensionado com área útil mínima de {area_duto_m2} m² (velocidade de {v_adotada} m/s)."
    )
    recomendacoes.append(
        f"Ventilador centrífugo de pressurização: vazão de projeto de {vazao_nominal_m3_h} m³/h a {pressao_estatica_total} Pa, com motor de {motor_adotado_cv} cv."
    )
    recomendacoes.append(
        "A tomada de ar externo deve ser instalada no nível do solo ou cobertura livre de risco de captação de fumaça."
    )

    return ResultadoDimensionamento(
        nome_edificio=dados.nome_edificio,
        tipo_escada=dados.tipo_escada,
        estagio1=res_estagio1,
        estagio2=res_estagio2,
        duto=res_duto,
        ventilador=res_ventilador,
        forca_abertura_porta_n=forca_abertura_total_n,
        conformidade_forca_abertura=conforme_forca,
        alertas=tuple(alertas),
        recomendacoes=tuple(recomendacoes),
    )
