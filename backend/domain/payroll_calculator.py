"""
Módulo de cálculos de folha de pagamento para Pessoa Jurídica (PJ)

Este módulo contém funções puras para cálculo de valores de folha de pagamento
seguindo regras contratuais customizadas que incluem conceitos como horas extras,
DSR e adicional noturno (não obrigatórios legalmente para PJ, apenas contratuais).

IMPORTANTE: Este sistema é para PJ (Pessoa Jurídica), não CLT.
Os conceitos de "horas extras" e "DSR" são tratados apenas como regras
contratuais/comerciais, sem amparo legal trabalhista.
"""

from decimal import Decimal
from typing import Dict


# ==============================================================================
# CONSTANTES PADRÃO
# ==============================================================================

CARGA_HORARIA_PADRAO = 220  # horas/mês
PERCENTUAL_ADIANTAMENTO_PADRAO = Decimal('40.00')  # 40%
MULTIPLICADOR_HORA_EXTRA_50 = Decimal('1.5')
MULTIPLICADOR_FERIADO = Decimal('2.0')
PERCENTUAL_DSR = Decimal('0.166667')  # 1/6 = 16,67%
PERCENTUAL_ADICIONAL_NOTURNO = Decimal('0.20')  # 20%


# ==============================================================================
# FUNÇÕES BASE
# ==============================================================================

def calcular_valor_hora(
    valor_contrato_mensal: Decimal,
    carga_horaria_mensal: int = CARGA_HORARIA_PADRAO
) -> Decimal:
    """
    Calcula o valor da hora contratual.
    
    Args:
        valor_contrato_mensal: Valor mensal acordado no contrato PJ
        carga_horaria_mensal: Carga horária mensal de referência (padrão 220h)
    
    Returns:
        Valor por hora trabalhada
        
    Exemplo:
        >>> calcular_valor_hora(Decimal('2200'), 220)
        Decimal('10.00')
    """
    if valor_contrato_mensal <= 0:
        raise ValueError("Valor do contrato deve ser maior que zero")
    if carga_horaria_mensal <= 0:
        raise ValueError("Carga horária deve ser maior que zero")
    
    return (valor_contrato_mensal / Decimal(carga_horaria_mensal)).quantize(Decimal('0.01'))


def calcular_adiantamento(
    valor_contrato_mensal: Decimal,
    percentual: Decimal = PERCENTUAL_ADIANTAMENTO_PADRAO
) -> Decimal:
    """
    Calcula o valor do adiantamento quinzenal.
    
    Args:
        valor_contrato_mensal: Valor mensal do contrato
        percentual: Percentual de adiantamento (padrão 40%)
    
    Returns:
        Valor do adiantamento
        
    Exemplo:
        >>> calcular_adiantamento(Decimal('2200'), Decimal('40'))
        Decimal('880.00')
    """
    if percentual < 0 or percentual > 100:
        raise ValueError("Percentual deve estar entre 0 e 100")
    
    return ((valor_contrato_mensal * percentual) / Decimal('100')).quantize(Decimal('0.01'))


def calcular_saldo_pos_adiantamento(
    valor_contrato_mensal: Decimal,
    valor_adiantamento: Decimal
) -> Decimal:
    """
    Calcula o saldo a pagar após o adiantamento.
    
    Args:
        valor_contrato_mensal: Valor mensal do contrato
        valor_adiantamento: Valor já pago como adiantamento
    
    Returns:
        Saldo para pagamento final do mês
        
    Exemplo:
        >>> calcular_saldo_pos_adiantamento(Decimal('2200'), Decimal('880'))
        Decimal('1320.00')
    """
    return (valor_contrato_mensal - valor_adiantamento).quantize(Decimal('0.01'))


# ==============================================================================
# PROVENTOS (VALORES A RECEBER)
# ==============================================================================

def calcular_hora_extra_50(
    horas_extras: Decimal,
    valor_hora: Decimal
) -> Decimal:
    """
    Calcula o valor das horas extras com 50% de adicional (regra contratual).
    
    Args:
        horas_extras: Quantidade de horas extras trabalhadas
        valor_hora: Valor da hora normal
    
    Returns:
        Valor total das horas extras
        
    Exemplo:
        >>> calcular_hora_extra_50(Decimal('10'), Decimal('10'))
        Decimal('150.00')
    """
    if horas_extras < 0:
        raise ValueError("Horas extras não podem ser negativas")
    
    valor_hora_extra = valor_hora * MULTIPLICADOR_HORA_EXTRA_50
    return (horas_extras * valor_hora_extra).quantize(Decimal('0.01'))


def calcular_hora_feriado(
    horas_feriado: Decimal,
    valor_hora: Decimal
) -> Decimal:
    """
    Calcula o valor das horas trabalhadas em feriados com 100% de adicional.
    
    Args:
        horas_feriado: Quantidade de horas trabalhadas em feriados
        valor_hora: Valor da hora normal
    
    Returns:
        Valor total das horas em feriados
        
    Exemplo:
        >>> calcular_hora_feriado(Decimal('8'), Decimal('10'))
        Decimal('160.00')
    """
    if horas_feriado < 0:
        raise ValueError("Horas de feriado não podem ser negativas")
    
    valor_hora_feriado = valor_hora * MULTIPLICADOR_FERIADO
    return (horas_feriado * valor_hora_feriado).quantize(Decimal('0.01'))


def calcular_adicional_noturno(
    horas_noturnas: Decimal,
    valor_hora: Decimal
) -> Decimal:
    """
    Calcula o adicional noturno (20% sobre a hora normal).
    
    Args:
        horas_noturnas: Quantidade de horas trabalhadas no período noturno
        valor_hora: Valor da hora normal
    
    Returns:
        Valor total do adicional noturno
        
    Exemplo:
        >>> calcular_adicional_noturno(Decimal('20'), Decimal('10'))
        Decimal('40.00')
    """
    if horas_noturnas < 0:
        raise ValueError("Horas noturnas não podem ser negativas")
    
    valor_adicional = valor_hora * PERCENTUAL_ADICIONAL_NOTURNO
    return (horas_noturnas * valor_adicional).quantize(Decimal('0.01'))


def calcular_dsr(
    total_horas_extras: Decimal,
    percentual: Decimal = PERCENTUAL_DSR
) -> Decimal:
    """
    Calcula o DSR (Descanso Semanal Remunerado) sobre horas extras.
    
    ATENÇÃO: DSR não é obrigação legal para PJ, tratado aqui como regra contratual.
    
    Args:
        total_horas_extras: Valor total das horas extras (não quantidade, mas valor em R$)
        percentual: Percentual de DSR (padrão 16.67% = 1/6)
    
    Returns:
        Valor do DSR sobre as horas extras
        
    Exemplo:
        >>> calcular_dsr(Decimal('150'))
        Decimal('25.00')
    """
    return (total_horas_extras * percentual).quantize(Decimal('0.01'))


def calcular_total_proventos(
    saldo_pos_adiantamento: Decimal,
    valor_hora_extra: Decimal,
    valor_feriado: Decimal,
    valor_dsr: Decimal,
    valor_adicional_noturno: Decimal
) -> Decimal:
    """
    Calcula o total de proventos (valores a receber).
    
    Args:
        saldo_pos_adiantamento: Saldo do salário após adiantamento
        valor_hora_extra: Total de horas extras
        valor_feriado: Total de feriados trabalhados
        valor_dsr: Total de DSR
        valor_adicional_noturno: Total de adicional noturno
    
    Returns:
        Soma de todos os proventos
        
    Exemplo:
        >>> calcular_total_proventos(
        ...     Decimal('1320'), Decimal('150'), Decimal('160'),
        ...     Decimal('25'), Decimal('40')
        ... )
        Decimal('1695.00')
    """
    total = (
        saldo_pos_adiantamento +
        valor_hora_extra +
        valor_feriado +
        valor_dsr +
        valor_adicional_noturno
    )
    return total.quantize(Decimal('0.01'))


# ==============================================================================
# DESCONTOS (VALORES A DEDUZIR)
# ==============================================================================

def calcular_desconto_atraso(
    minutos_atraso: int,
    valor_hora: Decimal
) -> Decimal:
    """
    Calcula o desconto por atrasos (proporcional por minuto).
    
    Args:
        minutos_atraso: Total de minutos de atraso no mês
        valor_hora: Valor da hora normal
    
    Returns:
        Valor a descontar por atrasos
        
    Exemplo:
        >>> calcular_desconto_atraso(30, Decimal('10'))
        Decimal('5.00')
    """
    if minutos_atraso < 0:
        raise ValueError("Minutos de atraso não podem ser negativos")
    
    horas_atraso = Decimal(minutos_atraso) / Decimal('60')
    return (horas_atraso * valor_hora).quantize(Decimal('0.01'))


def calcular_desconto_falta(
    horas_falta: Decimal,
    valor_hora: Decimal
) -> Decimal:
    """
    Calcula o desconto por faltas.
    
    Args:
        horas_falta: Total de horas de falta
        valor_hora: Valor da hora normal
    
    Returns:
        Valor a descontar por faltas
        
    Exemplo:
        >>> calcular_desconto_falta(Decimal('8'), Decimal('10'))
        Decimal('80.00')
    """
    if horas_falta < 0:
        raise ValueError("Horas de falta não podem ser negativas")
    
    return (horas_falta * valor_hora).quantize(Decimal('0.01'))


def calcular_dsr_sobre_faltas(
    valor_desconto_falta: Decimal,
    percentual: Decimal = PERCENTUAL_DSR
) -> Decimal:
    """
    Calcula o DSR sobre faltas (desconto adicional).
    
    Args:
        valor_desconto_falta: Valor já calculado do desconto de falta
        percentual: Percentual de DSR (padrão 16.67%)
    
    Returns:
        Valor do DSR a descontar sobre as faltas
        
    Exemplo:
        >>> calcular_dsr_sobre_faltas(Decimal('80'))
        Decimal('13.33')
    """
    return (valor_desconto_falta * percentual).quantize(Decimal('0.01'))


def calcular_total_descontos(
    desconto_atraso: Decimal,
    desconto_falta: Decimal,
    dsr_sobre_faltas: Decimal,
    vale_transporte: Decimal,
    descontos_manuais: Decimal
) -> Decimal:
    """
    Calcula o total de descontos.
    
    Args:
        desconto_atraso: Desconto por atrasos
        desconto_falta: Desconto por faltas
        dsr_sobre_faltas: DSR sobre faltas
        vale_transporte: Valor do VT a descontar
        descontos_manuais: Outros descontos manuais
    
    Returns:
        Soma de todos os descontos
        
    Exemplo:
        >>> calcular_total_descontos(
        ...     Decimal('5'), Decimal('80'), Decimal('13.33'),
        ...     Decimal('202.40'), Decimal('0')
        ... )
        Decimal('300.73')
    """
    total = (
        desconto_atraso +
        desconto_falta +
        dsr_sobre_faltas +
        vale_transporte +
        descontos_manuais
    )
    return total.quantize(Decimal('0.01'))


# ==============================================================================
# VALOR FINAL
# ==============================================================================

def calcular_valor_liquido(
    total_proventos: Decimal,
    total_descontos: Decimal
) -> Decimal:
    """
    Calcula o valor líquido a pagar.
    
    Args:
        total_proventos: Soma de todos os proventos
        total_descontos: Soma de todos os descontos
    
    Returns:
        Valor líquido final (proventos - descontos)
        
    Exemplo:
        >>> calcular_valor_liquido(Decimal('1695'), Decimal('300.73'))
        Decimal('1394.27')
    """
    return (total_proventos - total_descontos).quantize(Decimal('0.01'))


# ==============================================================================
# VALIDAÇÕES
# ==============================================================================

def validar_dados_entrada(dados: Dict) -> Dict[str, any]:
    """
    Valida os dados de entrada para cálculo da folha.
    
    Args:
        dados: Dicionário com todos os dados de entrada
    
    Returns:
        Dict com 'valido' (bool) e 'erros' (list)
        
    Exemplo:
        >>> validar_dados_entrada({
        ...     'valor_contrato_mensal': Decimal('2200'),
        ...     'horas_extras': Decimal('10'),
        ...     'minutos_atraso': 30
        ... })
        {'valido': True, 'erros': []}
    """
    erros = []
    
    # Valores monetários
    if dados.get('valor_contrato_mensal', 0) <= 0:
        erros.append("Valor do contrato deve ser maior que zero")
    
    # Horas
    if dados.get('horas_extras', 0) < 0:
        erros.append("Horas extras não podem ser negativas")
    if dados.get('horas_feriado', 0) < 0:
        erros.append("Horas de feriado não podem ser negativas")
    if dados.get('horas_noturnas', 0) < 0:
        erros.append("Horas noturnas não podem ser negativas")
    if dados.get('horas_falta', 0) < 0:
        erros.append("Horas de falta não podem ser negativas")
    
    # Minutos
    if dados.get('minutos_atraso', 0) < 0:
        erros.append("Minutos de atraso não podem ser negativos")
    
    # Percentuais
    percentual_adiantamento = dados.get('percentual_adiantamento', 40)
    if percentual_adiantamento < 0 or percentual_adiantamento > 100:
        erros.append("Percentual de adiantamento deve estar entre 0 e 100")
    
    # Adiantamento vs salário
    if dados.get('valor_adiantamento', 0) > dados.get('valor_contrato_mensal', 0):
        erros.append("Adiantamento não pode ser maior que o valor do contrato")
    
    return {
        'valido': len(erros) == 0,
        'erros': erros
    }


# ==============================================================================
# FUNÇÃO PRINCIPAL (CALCULA TUDO)
# ==============================================================================

def calcular_folha_completa(
    valor_contrato_mensal: Decimal,
    percentual_adiantamento: Decimal = PERCENTUAL_ADIANTAMENTO_PADRAO,
    horas_extras: Decimal = Decimal('0'),
    horas_feriado: Decimal = Decimal('0'),
    horas_noturnas: Decimal = Decimal('0'),
    minutos_atraso: int = 0,
    horas_falta: Decimal = Decimal('0'),
    vale_transporte: Decimal = Decimal('0'),
    descontos_manuais: Decimal = Decimal('0'),
    carga_horaria_mensal: int = CARGA_HORARIA_PADRAO
) -> Dict[str, Decimal]:
    """
    Calcula todos os valores da folha de pagamento PJ de uma só vez.
    
    Args:
        valor_contrato_mensal: Valor mensal do contrato
        percentual_adiantamento: % de adiantamento (padrão 40%)
        horas_extras: Horas extras 50%
        horas_feriado: Horas trabalhadas em feriados
        horas_noturnas: Horas com adicional noturno
        minutos_atraso: Total de minutos de atraso
        horas_falta: Total de horas de falta
        vale_transporte: Valor do VT
        descontos_manuais: Outros descontos
        carga_horaria_mensal: Carga horária (padrão 220h)
    
    Returns:
        Dicionário completo com todos os valores calculados
    """
    # Validar dados
    validacao = validar_dados_entrada({
        'valor_contrato_mensal': valor_contrato_mensal,
        'horas_extras': horas_extras,
        'horas_feriado': horas_feriado,
        'horas_noturnas': horas_noturnas,
        'minutos_atraso': minutos_atraso,
        'horas_falta': horas_falta,
        'percentual_adiantamento': percentual_adiantamento,
        'valor_adiantamento': calcular_adiantamento(valor_contrato_mensal, percentual_adiantamento)
    })
    
    if not validacao['valido']:
        raise ValueError(f"Dados inválidos: {', '.join(validacao['erros'])}")
    
    # Cálculos base
    valor_hora = calcular_valor_hora(valor_contrato_mensal, carga_horaria_mensal)
    adiantamento = calcular_adiantamento(valor_contrato_mensal, percentual_adiantamento)
    saldo = calcular_saldo_pos_adiantamento(valor_contrato_mensal, adiantamento)
    
    # Proventos
    hora_extra_valor = calcular_hora_extra_50(horas_extras, valor_hora)
    feriado_valor = calcular_hora_feriado(horas_feriado, valor_hora)
    noturno_valor = calcular_adicional_noturno(horas_noturnas, valor_hora)
    dsr_valor = calcular_dsr(hora_extra_valor)
    
    total_proventos = calcular_total_proventos(
        saldo, hora_extra_valor, feriado_valor, dsr_valor, noturno_valor
    )
    
    # Descontos
    atraso_desconto = calcular_desconto_atraso(minutos_atraso, valor_hora)
    falta_desconto = calcular_desconto_falta(horas_falta, valor_hora)
    dsr_falta = calcular_dsr_sobre_faltas(falta_desconto)
    
    total_descontos_calc = calcular_total_descontos(
        atraso_desconto, falta_desconto, dsr_falta, vale_transporte, descontos_manuais
    )
    
    # Valor final
    liquido = calcular_valor_liquido(total_proventos, total_descontos_calc)
    
    return {
        # Base
        'valor_hora': valor_hora,
        'adiantamento': adiantamento,
        'saldo_pos_adiantamento': saldo,
        
        # Proventos
        'hora_extra_50': hora_extra_valor,
        'feriado_trabalhado': feriado_valor,
        'adicional_noturno': noturno_valor,
        'dsr': dsr_valor,
        'total_proventos': total_proventos,
        
        # Descontos
        'desconto_atraso': atraso_desconto,
        'desconto_falta': falta_desconto,
        'dsr_sobre_faltas': dsr_falta,
        'vale_transporte': vale_transporte,
        'descontos_manuais': descontos_manuais,
        'total_descontos': total_descontos_calc,
        
        # Final
        'valor_bruto': total_proventos,
        'valor_liquido': liquido
    }
