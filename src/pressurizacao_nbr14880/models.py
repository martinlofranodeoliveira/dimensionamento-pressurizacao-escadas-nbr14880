"""Modelos de dados e estruturas imutáveis para pressurização de escadas NBR 14880."""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction


class TipoEscada(str, Enum):
    """Classificação da escada de segurança segundo enclausuramento."""
    ENCLAUSURADA_PROTEGIDA = "enclausurada_protegida"
    COM_ANTECAMARA = "com_antecamara"
    PRESSURIZADA_DIRETA = "pressurizada_direta"


class TipoDuto(str, Enum):
    """Material construtivo do duto vertical de injeção de ar."""
    METALICO_GALVANIZADO = "metalico_galvanizado"
    ALVENARIA_CONCRETO = "alvenaria_concreto"


class TipoPorta(str, Enum):
    """Tipologia dimensional da porta corta-fogo de acesso à escada."""
    SIMPLES_PADRAO = "simples_padrao"
    DUPLA_PADRAO = "dupla_padrao"


@dataclass(frozen=True)
class DadosEdificacao:
    """Parâmetros geométricos e de projeto da edificação a pressurizar."""
    nome_edificio: str
    quantidade_pavimentos: int
    altura_total_m: Fraction
    tipo_escada: TipoEscada
    tipo_duto: TipoDuto
    possui_sprinklers: bool
    quantidade_portas_simples: int
    quantidade_portas_duplas: int
    portas_abertas_projeto: int
    perda_carga_distribuicao_pa: Fraction

    def __post_init__(self) -> None:
        if not self.nome_edificio or not self.nome_edificio.strip():
            raise ValueError("O nome da edificação não pode ser vazio.")
        if self.quantidade_pavimentos <= 0:
            raise ValueError(f"Quantidade de pavimentos inválida ({self.quantidade_pavimentos}). Deve ser >= 1.")
        if self.altura_total_m <= Fraction(0, 1):
            raise ValueError(f"Altura total ({self.altura_total_m}m) deve ser estritamente positiva.")
        if (self.quantidade_portas_simples + self.quantidade_portas_duplas) <= 0:
            raise ValueError("A edificação deve possuir ao menos uma porta de acesso à escada.")
        if self.perda_carga_distribuicao_pa < Fraction(0, 1):
            raise ValueError("A perda de carga de distribuição não pode ser negativa.")


@dataclass(frozen=True)
class ResultadoEstagio1:
    """Estágio 1: Portas Fechadas (Garantia de Sobrepressão 50 Pa)."""
    pressao_diferencial_pa: Fraction
    area_total_frestas_m2: Fraction
    vazao_frestas_m3_s: Fraction
    vazao_frestas_m3_h: Fraction


@dataclass(frozen=True)
class ResultadoEstagio2:
    """Estágio 2: Portas Abertas (Velocidade de Escape contra Fumaça)."""
    velocidade_escape_m_s: Fraction
    portas_abertas: int
    area_abertura_total_m2: Fraction
    vazao_portas_abertas_m3_s: Fraction
    vazao_portas_fechadas_m3_s: Fraction
    vazao_total_estagio2_m3_s: Fraction
    vazao_total_estagio2_m3_h: Fraction


@dataclass(frozen=True)
class ResultadoDuto:
    """Dimensionamento aerodinâmico do duto vertical de ar."""
    tipo_duto: TipoDuto
    velocidade_maxima_permitida_m_s: Fraction
    velocidade_adotada_m_s: Fraction
    area_util_minima_m2: Fraction
    dimensao_sugerida: str


@dataclass(frozen=True)
class ResultadoVentilador:
    """Seleção aerodinâmica e potência eletromecânica do ventilador."""
    vazao_nominal_m3_s: Fraction
    vazao_nominal_m3_h: Fraction
    pressao_estatica_total_pa: Fraction
    rendimento_aerodinamico: Fraction
    potencia_eixo_w: Fraction
    potencia_motor_calculada_cv: Fraction
    motor_comercial_adotado_cv: Fraction


@dataclass(frozen=True)
class ResultadoDimensionamento:
    """Resultado técnico completo consolidado da ABNT NBR 14880:2014."""
    nome_edificio: str
    tipo_escada: TipoEscada
    estagio1: ResultadoEstagio1
    estagio2: ResultadoEstagio2
    duto: ResultadoDuto
    ventilador: ResultadoVentilador
    forca_abertura_porta_n: Fraction
    conformidade_forca_abertura: bool
    alertas: tuple[str, ...]
    recomendacoes: tuple[str, ...]
