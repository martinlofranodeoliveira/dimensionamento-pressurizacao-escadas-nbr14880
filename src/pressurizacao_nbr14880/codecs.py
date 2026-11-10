"""Codec JSON canônico RFC 8259 para dimensionamento de pressurização NBR 14880."""

import json
from fractions import Fraction
from typing import Any

from pressurizacao_nbr14880.models import (
    DadosEdificacao,
    ResultadoDimensionamento,
    TipoDuto,
    TipoEscada,
)


def _rejeitar_float(valor: str) -> None:
    raise ValueError(f"Ponto flutuante ({valor}) não é permitido. Utilize inteiros ou strings decimais exatas.")


def _rejeitar_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError(f"Chave duplicada encontrada no JSON: '{chave}'")
        resultado[chave] = valor
    return resultado


def _verificar_profundidade(obj: Any, profundidade: int = 1, limite: int = 32) -> None:
    if profundidade > limite:
        raise ValueError(f"Profundidade da estrutura JSON ({profundidade}) excede o limite máximo permitido de {limite}.")
    if isinstance(obj, dict):
        for v in obj.values():
            _verificar_profundidade(v, profundidade + 1, limite)
    elif isinstance(obj, list):
        for elem in obj:
            _verificar_profundidade(elem, profundidade + 1, limite)


def _para_fracao(val: Any) -> Fraction:
    if isinstance(val, (int, str)):
        return Fraction(val)
    if isinstance(val, Fraction):
        return val
    raise ValueError(f"Tipo inválido para conversão fracionária: {type(val).__name__} ({val})")


def carregar_dados_edificacao_json(conteudo: str) -> DadosEdificacao:
    """Carrega e valida os dados de pressurização em JSON canônico sem float."""
    if conteudo.startswith(("\ufeff", "\xef\xbb\xbf")):
        raise ValueError("Byte Order Mark (BOM) detectado. O arquivo deve ser codificado estritamente em UTF-8 puro.")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_rejeitar_chaves_duplicadas,
            parse_float=_rejeitar_float,
        )
    except json.JSONDecodeError as err:
        raise ValueError(f"Erro de decodificação JSON: {err}") from err

    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise ValueError("O JSON raiz deve ser um objeto dicionário.")

    nome = str(dados.get("nome_edificio", "Edifício sem nome"))
    qtd_pav = int(dados.get("quantidade_pavimentos", 1))
    altura = _para_fracao(dados.get("altura_total_m", "3.0"))

    tipo_escada_str = str(dados.get("tipo_escada", "enclausurada_protegida")).lower()
    try:
        tipo_escada = TipoEscada(tipo_escada_str)
    except ValueError:
        tipo_escada = TipoEscada.ENCLAUSURADA_PROTEGIDA

    tipo_duto_str = str(dados.get("tipo_duto", "metalico_galvanizado")).lower()
    try:
        tipo_duto = TipoDuto(tipo_duto_str)
    except ValueError:
        tipo_duto = TipoDuto.METALICO_GALVANIZADO

    possui_sprinklers = bool(dados.get("possui_sprinklers", False))
    portas_simples = int(dados.get("quantidade_portas_simples", qtd_pav))
    portas_duplas = int(dados.get("quantidade_portas_duplas", 0))
    portas_abertas = int(dados.get("portas_abertas_projeto", 1))
    perda_carga_dist = _para_fracao(dados.get("perda_carga_distribuicao_pa", 200))

    return DadosEdificacao(
        nome_edificio=nome,
        quantidade_pavimentos=qtd_pav,
        altura_total_m=altura,
        tipo_escada=tipo_escada,
        tipo_duto=tipo_duto,
        possui_sprinklers=possui_sprinklers,
        quantidade_portas_simples=portas_simples,
        quantidade_portas_duplas=portas_duplas,
        portas_abertas_projeto=portas_abertas,
        perda_carga_distribuicao_pa=perda_carga_dist,
    )


def _serializar_valor(val: Any) -> Any:
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return val.numerator
        return f"{val.numerator}/{val.denominator}"
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, tuple):
        return [_serializar_valor(x) for x in val]
    if isinstance(val, dict):
        return {k: _serializar_valor(v) for k, v in val.items()}
    return val


def exportar_resultado_json(res: ResultadoDimensionamento) -> str:
    """Serializa o resultado em JSON canônico RFC 8259 determinístico."""
    dados: dict[str, Any] = {
        "norma": "ABNT NBR 14880:2014",
        "nome_edificio": res.nome_edificio,
        "tipo_escada": res.tipo_escada.value,
        "forca_abertura_porta_n": _serializar_valor(res.forca_abertura_porta_n),
        "conformidade_forca_abertura": res.conformidade_forca_abertura,
        "estagio1": {
            "pressao_diferencial_pa": _serializar_valor(res.estagio1.pressao_diferencial_pa),
            "area_total_frestas_m2": _serializar_valor(res.estagio1.area_total_frestas_m2),
            "vazao_frestas_m3_s": _serializar_valor(res.estagio1.vazao_frestas_m3_s),
            "vazao_frestas_m3_h": _serializar_valor(res.estagio1.vazao_frestas_m3_h),
        },
        "estagio2": {
            "velocidade_escape_m_s": _serializar_valor(res.estagio2.velocidade_escape_m_s),
            "portas_abertas": res.estagio2.portas_abertas,
            "area_abertura_total_m2": _serializar_valor(res.estagio2.area_abertura_total_m2),
            "vazao_portas_abertas_m3_s": _serializar_valor(res.estagio2.vazao_portas_abertas_m3_s),
            "vazao_portas_fechadas_m3_s": _serializar_valor(res.estagio2.vazao_portas_fechadas_m3_s),
            "vazao_total_estagio2_m3_s": _serializar_valor(res.estagio2.vazao_total_estagio2_m3_s),
            "vazao_total_estagio2_m3_h": _serializar_valor(res.estagio2.vazao_total_estagio2_m3_h),
        },
        "duto": {
            "tipo_duto": res.duto.tipo_duto.value,
            "velocidade_maxima_permitida_m_s": _serializar_valor(res.duto.velocidade_maxima_permitida_m_s),
            "velocidade_adotada_m_s": _serializar_valor(res.duto.velocidade_adotada_m_s),
            "area_util_minima_m2": _serializar_valor(res.duto.area_util_minima_m2),
            "dimensao_sugerida": res.duto.dimensao_sugerida,
        },
        "ventilador": {
            "vazao_nominal_m3_s": _serializar_valor(res.ventilador.vazao_nominal_m3_s),
            "vazao_nominal_m3_h": _serializar_valor(res.ventilador.vazao_nominal_m3_h),
            "pressao_estatica_total_pa": _serializar_valor(res.ventilador.pressao_estatica_total_pa),
            "rendimento_aerodinamico": _serializar_valor(res.ventilador.rendimento_aerodinamico),
            "potencia_eixo_w": _serializar_valor(res.ventilador.potencia_eixo_w),
            "potencia_motor_calculada_cv": _serializar_valor(res.ventilador.potencia_motor_calculada_cv),
            "motor_comercial_adotado_cv": _serializar_valor(res.ventilador.motor_comercial_adotado_cv),
        },
        "alertas": list(res.alertas),
        "recomendacoes": list(res.recomendacoes),
    }

    return json.dumps(dados, indent=2, sort_keys=True, ensure_ascii=False)
