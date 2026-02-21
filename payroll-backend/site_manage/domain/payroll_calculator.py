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
from calendar import monthrange


# ==============================================================================
# CONSTANTES PADRÃO (Legado/Defaults)
# ==============================================================================

CARGA_HORARIA_PADRAO = 220  # horas/mês
PERCENTUAL_ADIANTAMENTO_PADRAO = Decimal("40.00")  # 40%

# Defaults para retrocompatibilidade
DEFAULT_MULT_HORA_EXTRA = Decimal("1.5")
DEFAULT_MULT_FERIADO = Decimal("2.0")
DEFAULT_MULT_NOTURNO = Decimal("1.20")


# ==============================================================================
# FUNÇÕES BASE
# ==============================================================================


def calcular_salario_proporcional(
    salario_mensal: Decimal,
    data_inicio,  # date object
    reference_month: str,
) -> tuple:
    """
    Calcula salário proporcional baseado na data de início do trabalho no mês.

    Quando um funcionário inicia no meio do mês, o salário deve ser proporcional
    aos dias efetivamente trabalhados.

    Args:
        salario_mensal: Salário mensal cheio contratado
        data_inicio: Data que o funcionário começou (objeto date)
        reference_month: Mês de referência (formato: MM/YYYY ou YYYY-MM)

    Returns:
        Tupla com (salario_proporcional, dias_trabalhados, dias_totais_mes)

    Raises:
        ValueError: Se a data de início não pertence ao mês de referência

    Exemplo:
        >>> from datetime import date
        >>> # Funcionário iniciou dia 20/01, mês tem 31 dias
        >>> calcular_salario_proporcional(Decimal('2200'), date(2026, 1, 20), '01/2026')
        (Decimal('851.61'), 12, 31)  # 12 dias trabalhados de 31
    """
    # Parsear reference_month
    if "/" in reference_month:
        mes, ano = reference_month.split("/")
        mes = int(mes)
        ano = int(ano)
    else:
        ano, mes = reference_month.split("-")
        ano = int(ano)
        mes = int(mes)

    # Verificar se a data de início está no mês correto
    if data_inicio.month != mes or data_inicio.year != ano:
        raise ValueError(
            f"Data de início {data_inicio} não pertence ao mês {reference_month}"
        )

    # Calcular dias totais do mês
    dias_totais_mes = monthrange(ano, mes)[1]

    # Calcular dias trabalhados (do dia de início até o final do mês, inclusive)
    # Exemplo: iniciou dia 20, mês tem 31 dias → trabalhou dias 20, 21, ..., 31 = 12 dias
    dias_trabalhados = dias_totais_mes - data_inicio.day + 1

    # Calcular salário proporcional
    # Fórmula: (salário × dias_trabalhados) / dias_totais_mes
    salario_proporcional = (
        salario_mensal * Decimal(dias_trabalhados) / Decimal(dias_totais_mes)
    ).quantize(Decimal("0.01"))

    return salario_proporcional, dias_trabalhados, dias_totais_mes


def calcular_dias_trabalhados(
    reference_month: str,
    absence_days: int = 0,
    hired_date=None,
) -> int:
    """
    Calcula dias efetivamente trabalhados considerando faltas e admissão mid-month.

    Esta função integra-se com o cálculo de Vale Transporte, pois o VT deve ser
    proporcional aos dias que o colaborador efetivamente compareceu ao trabalho.

    Args:
        reference_month: Mês de referência (MM/YYYY ou YYYY-MM)
        absence_days: Número de dias de falta no mês
        hired_date: Data de admissão (date object), se admitido no meio do mês

    Returns:
        Número de dias efetivamente trabalhados (para fins de VT)

    Raises:
        ValueError: Se dados inválidos

    Exemplo:
        >>> # Mês normal, sem faltas, sem admissão mid-month
        >>> calcular_dias_trabalhados('01/2026')
        25  # 25 dias úteis em janeiro/2026

        >>> # Mês com 1 falta
        >>> calcular_dias_trabalhados('01/2026', absence_days=1)
        24  # 25 - 1 = 24 dias

        >>> # Admitido dia 20 (12 dias restantes)
        >>> from datetime import date
        >>> calcular_dias_trabalhados('01/2026', hired_date=date(2026, 1, 20))
        12  # Trabalhou apenas de 20 a 31
    """

    if absence_days < 0:
        raise ValueError("Dias de falta não podem ser negativos")

    # Parse reference month
    if "/" in reference_month:
        mes, ano = reference_month.split("/")
        mes, ano = int(mes), int(ano)
    else:
        ano, mes = reference_month.split("-")
        ano, mes = int(ano), int(mes)

    # Get total business days in month
    # Import here to avoid circular dependency
    from site_manage.application.commands.payroll_service import calcular_dias_mes

    # calcular_dias_mes returns (dias_uteis, domingos_e_feriados)
    # We need format as string for the function
    reference_str = f"{mes:02d}/{ano}" if "/" in reference_month else f"{ano}-{mes:02d}"
    dias_uteis, _ = calcular_dias_mes(reference_str)

    # If hired mid-month, calculate proportional worked days
    if hired_date:
        # Use proportional salary function to get worked calendar days
        _, worked_calendar_days, total_calendar_days = calcular_salario_proporcional(
            Decimal("0"),  # Dummy value
            hired_date,
            reference_month,
        )

        # Convert to proportional business days
        # Example: worked 12 of 31 calendar days → ~10 of 25 business days
        dias_uteis = int((worked_calendar_days / total_calendar_days) * dias_uteis)

    # Subtract absences
    dias_trabalhados = max(0, dias_uteis - absence_days)

    return dias_trabalhados


def calcular_vale_transporte(
    viagens_por_dia: int,
    tarifa_passagem: Decimal,
    dias_trabalhados: int,
) -> Decimal:
    """
    Calcula o valor do Vale Transporte baseado em dias efetivamente trabalhados.

    Fórmula: VT = viagens_por_dia × tarifa × dias_trabalhados

    Esta é a nova lógica dinâmica que substitui o valor fixo mensal.
    O VT é automaticamente ajustado quando há faltas ou admissão mid-month.

    Args:
        viagens_por_dia: Número de viagens por dia (2, 4, ou 6)
            - 2: Apenas ida OU volta (casos especiais)
            - 4: Ida e volta, 2 transportes cada (padrão)
            - 6: Casos especiais (integração, 3 transportes)
        tarifa_passagem: Valor da passagem de ônibus (ex: R$ 4,60 em Belém)
        dias_trabalhados: Dias que o colaborador efetivamente compareceu

    Returns:
        Valor total do VT a ser descontado

    Raises:
        ValueError: Se parâmetros inválidos

    Exemplos:
        >>> # Mês completo, 4 viagens/dia (ida e volta)
        >>> calcular_vale_transporte(4, Decimal('4.60'), 22)
        Decimal('404.80')  # 4 × 4.60 × 22

        >>> # Com 1 falta
        >>> calcular_vale_transporte(4, Decimal('4.60'), 21)
        Decimal('386.40')  # 4 × 4.60 × 21

        >>> # Admissão mid-month (11 dias)
        >>> calcular_vale_transporte(4, Decimal('4.60'), 11)
        Dec imal('202.40')  # 4 × 4.60 × 11
    """
    # Validations
    if viagens_por_dia <= 0:
        raise ValueError("viagens_por_dia must be a positive integer")

    if tarifa_passagem <= 0:
        raise ValueError("tarifa_passagem must be positive")

    if dias_trabalhados < 0:
        raise ValueError("dias_trabalhados cannot be negative")

    # Calculate VT
    vt_total = (
        Decimal(viagens_por_dia) * tarifa_passagem * Decimal(dias_trabalhados)
    ).quantize(Decimal("0.01"))

    return vt_total


def calcular_estorno_vt(
    viagens_por_dia: int,
    tarifa_passagem: Decimal,
    dias_falta: int,
) -> Decimal:
    """
    Calcula o estorno de Vale Transporte baseado nos dias de falta.

    O VT é considerado um benefício pago à parte/antecipado.
    Na folha, apenas descontamos (estornamos) o valor referente aos dias NÃO trabalhados.

    Fórmula: Estorno = viagens_por_dia × tarifa × dias_falta

    Args:
        viagens_por_dia: Número de viagens por dia
        tarifa_passagem: Valor da passagem
        dias_falta: Número de dias que o colaborador faltou

    Returns:
        Valor a ser descontado (estornado) da folha
    """
    if dias_falta <= 0:
        return Decimal("0.00")

    if viagens_por_dia <= 0 or tarifa_passagem <= 0:
        return Decimal("0.00")

    estorno = (
        Decimal(viagens_por_dia) * tarifa_passagem * Decimal(dias_falta)
    ).quantize(Decimal("0.01"))

    return estorno


def calcular_valor_hora(
    valor_contrato_mensal: Decimal, carga_horaria_mensal: int = CARGA_HORARIA_PADRAO
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

    return (valor_contrato_mensal / Decimal(carga_horaria_mensal)).quantize(
        Decimal("0.01")
    )


def calcular_adiantamento(
    valor_contrato_mensal: Decimal, percentual: Decimal = PERCENTUAL_ADIANTAMENTO_PADRAO
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

    return ((valor_contrato_mensal * percentual) / Decimal("100")).quantize(
        Decimal("0.01")
    )


def calcular_saldo_pos_adiantamento(
    valor_contrato_mensal: Decimal, valor_adiantamento: Decimal
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
    return (valor_contrato_mensal - valor_adiantamento).quantize(Decimal("0.01"))


# ==============================================================================
# PROVENTOS (VALORES A RECEBER)
# ==============================================================================


def calcular_hora_extra_50(
    horas_extras: Decimal,
    valor_hora: Decimal,
    multiplicador: Decimal = DEFAULT_MULT_HORA_EXTRA,
) -> Decimal:
    """
    Calcula o valor das horas extras.

    Args:
        horas_extras: Quantidade de horas extras
        valor_hora: Valor da hora normal
        multiplicador: Fator de multiplicação (ex: 1.5 para 50%, 2.0 para 100%)
    """
    if horas_extras < 0:
        raise ValueError("Horas extras não podem ser negativas")

    if multiplicador < 1:
        # Permitir multiplicadores menores que 1? Geralmente hora extra é > 1.
        # Mas para flexibilidade, apenas logar ou aceitar.
        pass

    valor_hora_extra = valor_hora * multiplicador
    return (horas_extras * valor_hora_extra).quantize(Decimal("0.01"))


def calcular_hora_feriado(
    horas_feriado: Decimal,
    valor_hora: Decimal,
    multiplicador: Decimal = DEFAULT_MULT_FERIADO,
) -> Decimal:
    """
    Calcula o valor das horas trabalhadas em feriados.

    Args:
        horas_feriado: Quantidade de horas
        valor_hora: Valor da hora normal
        multiplicador: Fator de multiplicação (ex: 2.0 para 100%)
    """
    if horas_feriado < 0:
        raise ValueError("Horas de feriado não podem ser negativas")

    valor_hora_feriado = valor_hora * multiplicador
    return (horas_feriado * valor_hora_feriado).quantize(Decimal("0.01"))


def calcular_adicional_noturno(
    horas_noturnas: Decimal,
    valor_hora: Decimal,
    multiplicador: Decimal = DEFAULT_MULT_NOTURNO,
) -> Decimal:
    """
    Calcula o adicional noturno.

    Args:
        horas_noturnas: Quantidade de horas
        valor_hora: Valor da hora normal
        multiplicador: Fator de multiplicação (ex: 1.2 para 20%)
    """
    if horas_noturnas < 0:
        raise ValueError("Horas noturnas não podem ser negativas")

    valor_hora_noturna = valor_hora * multiplicador
    return (horas_noturnas * valor_hora_noturna).quantize(Decimal("0.01"))


def calcular_dsr(
    valor_horas_extras: Decimal,
    valor_feriados: Decimal,
    dias_uteis: int,
    domingos_e_feriados: int,
) -> Decimal:
    """
    Calcula o DSR (Descanso Semanal Remunerado) sobre horas extras e feriados.

    ATENÇÃO: DSR não é obrigação legal para PJ, tratado aqui como regra contratual.

    Fórmula: (Horas Extras + Feriados) / Dias Úteis * (Domingos + Feriados)

    Args:
        valor_horas_extras: Valor total das horas extras em R$
        valor_feriados: Valor total dos feriados trabalhados em R$
        dias_uteis: Número de dias úteis no mês
        domingos_e_feriados: Número de domingos + feriados no mês

    Returns:
        Valor do DSR

    Exemplo:
        >>> calcular_dsr(Decimal('220'), Decimal('160'), 25, 6)
        Decimal('91.20')
    """
    if dias_uteis <= 0:
        raise ValueError("Dias úteis deve ser maior que zero")

    total_extras = valor_horas_extras + valor_feriados
    if total_extras == 0:
        return Decimal("0.00")

    dsr_diario = total_extras / Decimal(dias_uteis)
    dsr_total = dsr_diario * Decimal(domingos_e_feriados)

    return dsr_total.quantize(Decimal("0.01"))


def calcular_total_proventos(
    saldo_pos_adiantamento: Decimal,
    valor_hora_extra: Decimal,
    valor_feriado: Decimal,
    valor_dsr: Decimal,
    valor_adicional_noturno: Decimal,
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
        saldo_pos_adiantamento
        + valor_hora_extra
        + valor_feriado
        + valor_dsr
        + valor_adicional_noturno
    )
    return total.quantize(Decimal("0.01"))


# ==============================================================================
# DESCONTOS (VALORES A DEDUZIR)
# ==============================================================================


def calcular_desconto_atraso(minutos_atraso: int, valor_hora: Decimal) -> Decimal:
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

    horas_atraso = Decimal(minutos_atraso) / Decimal("60")
    return (horas_atraso * valor_hora).quantize(Decimal("0.01"))


def calcular_desconto_falta(horas_falta: Decimal, valor_hora: Decimal) -> Decimal:
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

    return (horas_falta * valor_hora).quantize(Decimal("0.01"))


def calcular_desconto_falta_por_dia(
    dias_falta: int, valor_base_mensal: Decimal
) -> Decimal:
    """
    Calcula o desconto por faltas usando divisão por 30 dias FIXOS.

    IMPORTANTE: Sempre divide por 30, independente do mês ter 28, 30 ou 31 dias.
    Esta é a regra contratual definida pelo stakeholder.

    Args:
        dias_falta: Número de dias de falta
        valor_base_mensal: Salário base mensal

    Returns:
        Valor a descontar por faltas

    Exemplo:
        >>> calcular_desconto_falta_por_dia(1, Decimal('2200'))
        Decimal('73.33')  # R$ 2200 / 30 (sempre 30 dias)
    """
    if dias_falta < 0:
        raise ValueError("Dias de falta não podem ser negativos")

    # SEMPRE 30 dias, regra fixa
    valor_por_dia = valor_base_mensal / Decimal("30")
    return (valor_por_dia * Decimal(dias_falta)).quantize(Decimal("0.01"))


# DSR sobre faltas REMOVIDO - conceito CLT, não aplicável para PJ
# Sistema é PJ-only e não implementa regras trabalhistas CLT


def calcular_total_descontos(
    desconto_atraso: Decimal,
    desconto_falta: Decimal,
    vale_transporte: Decimal,
    descontos_manuais: Decimal,
) -> Decimal:
    """
    Calcula o total de descontos.

    IMPORTANTE: DSR sobre faltas NÃO é aplicado (conceito CLT, sistema é PJ-only).

    Args:
        desconto_atraso: Desconto por atrasos
        desconto_falta: Desconto por faltas
        vale_transporte: Valor do VT a descontar
        descontos_manuais: Outros descontos manuais

    Returns:
        Soma de todos os descontos

    Exemplo:
        >>> calcular_total_descontos(
        ...     Decimal('5'), Decimal('80'),
        ...     Decimal('202.40'), Decimal('0')
        ... )
        Decimal('287.40')
    """
    total = desconto_atraso + desconto_falta + vale_transporte + descontos_manuais
    return total.quantize(Decimal("0.01"))


# ==============================================================================
# VALOR FINAL
# ==============================================================================


def calcular_valor_liquido(
    total_proventos: Decimal, total_descontos: Decimal
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
    return (total_proventos - total_descontos).quantize(Decimal("0.01"))


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
    if dados.get("valor_contrato_mensal", 0) <= 0:
        erros.append("Valor do contrato deve ser maior que zero")

    # Horas
    if dados.get("horas_extras", 0) < 0:
        erros.append("Horas extras não podem ser negativas")
    if dados.get("horas_feriado", 0) < 0:
        erros.append("Horas de feriado não podem ser negativas")
    if dados.get("horas_noturnas", 0) < 0:
        erros.append("Horas noturnas não podem ser negativas")
    if dados.get("horas_falta", 0) < 0:
        erros.append("Horas de falta não podem ser negativas")

    # Minutos
    if dados.get("minutos_atraso", 0) < 0:
        erros.append("Minutos de atraso não podem ser negativos")

    # Percentuais
    percentual_adiantamento = dados.get("percentual_adiantamento", 40)
    if percentual_adiantamento < 0 or percentual_adiantamento > 100:
        erros.append("Percentual de adiantamento deve estar entre 0 e 100")

    # Adiantamento vs salário
    if dados.get("valor_adiantamento", 0) > dados.get("valor_contrato_mensal", 0):
        erros.append("Adiantamento não pode ser maior que o valor do contrato")

    return {"valido": len(erros) == 0, "erros": erros}


# ==============================================================================
# FUNÇÃO PRINCIPAL (CALCULA TUDO)
# ==============================================================================


def calcular_folha_completa(
    valor_contrato_mensal: Decimal,
    percentual_adiantamento: Decimal = PERCENTUAL_ADIANTAMENTO_PADRAO,
    horas_extras: Decimal = Decimal("0"),
    horas_feriado: Decimal = Decimal("0"),
    horas_noturnas: Decimal = Decimal("0"),
    minutos_atraso: int = 0,
    horas_falta: Decimal = Decimal("0"),
    vale_transporte: Decimal = Decimal("0"),
    descontos_manuais: Decimal = Decimal("0"),
    carga_horaria_mensal: int = CARGA_HORARIA_PADRAO,
    dias_uteis_mes: int = 22,
    domingos_e_feriados_mes: int = 8,
    # Novos parâmetros de configuração (com defaults para compatibilidade)
    multiplicador_extras: Decimal = DEFAULT_MULT_HORA_EXTRA,
    multiplicador_feriado: Decimal = DEFAULT_MULT_FERIADO,
    multiplicador_noturno: Decimal = DEFAULT_MULT_NOTURNO,
    absence_days: int = 0,  # Novo parâmetro para cálculo correto de faltas (1/30)
) -> Dict[str, Decimal]:
    """
    Calcula todos os valores da folha de pagamento PJ de uma só vez,
    respeitando as configurações da empresa.
    """
    # Validar dados
    validacao = validar_dados_entrada(
        {
            "valor_contrato_mensal": valor_contrato_mensal,
            "horas_extras": horas_extras,
            "horas_feriado": horas_feriado,
            "horas_noturnas": horas_noturnas,
            "minutos_atraso": minutos_atraso,
            "horas_falta": horas_falta,
            "percentual_adiantamento": percentual_adiantamento,
            "valor_adiantamento": calcular_adiantamento(
                valor_contrato_mensal, percentual_adiantamento
            ),
        }
    )

    if not validacao["valido"]:
        raise ValueError(f"Dados inválidos: {', '.join(validacao['erros'])}")

    # Cálculos base
    valor_hora = calcular_valor_hora(valor_contrato_mensal, carga_horaria_mensal)
    adiantamento = calcular_adiantamento(valor_contrato_mensal, percentual_adiantamento)
    saldo = calcular_saldo_pos_adiantamento(valor_contrato_mensal, adiantamento)

    # Proventos
    hora_extra_valor = calcular_hora_extra_50(
        horas_extras, valor_hora, multiplicador_extras
    )
    feriado_valor = calcular_hora_feriado(
        horas_feriado, valor_hora, multiplicador_feriado
    )
    noturno_valor = calcular_adicional_noturno(
        horas_noturnas, valor_hora, multiplicador_noturno
    )
    dsr_valor = calcular_dsr(
        hora_extra_valor, feriado_valor, dias_uteis_mes, domingos_e_feriados_mes
    )

    total_proventos = calcular_total_proventos(
        saldo, hora_extra_valor, feriado_valor, dsr_valor, noturno_valor
    )

    # Descontos (SEM DSR sobre faltas - conceito CLT)
    atraso_desconto = calcular_desconto_atraso(minutos_atraso, valor_hora)

    # Cálculo de Faltas: Prioriza absence_days (Regra 1/30), fallback para horas
    if absence_days > 0:
        falta_desconto = calcular_desconto_falta_por_dia(
            absence_days, valor_contrato_mensal
        )
    else:
        # Fallback / Compatibilidade
        falta_desconto = calcular_desconto_falta(horas_falta, valor_hora)

    total_descontos_calc = calcular_total_descontos(
        atraso_desconto, falta_desconto, vale_transporte, descontos_manuais
    )

    # Valor final
    liquido = calcular_valor_liquido(total_proventos, total_descontos_calc)

    return {
        # Base
        "valor_hora": valor_hora,
        "adiantamento": adiantamento,
        "saldo_pos_adiantamento": saldo,
        # Proventos
        "hora_extra_50": hora_extra_valor,
        "feriado_trabalhado": feriado_valor,
        "adicional_noturno": noturno_valor,
        "dsr": dsr_valor,
        "total_proventos": total_proventos,
        # Descontos
        "desconto_atraso": atraso_desconto,
        "desconto_falta": falta_desconto,
        # 'dsr_sobre_faltas': REMOVIDO - conceito CLT
        "vale_transporte": vale_transporte,
        "descontos_manuais": descontos_manuais,
        "total_descontos": total_descontos_calc,
        # Final
        "valor_bruto": total_proventos,
        "valor_liquido": liquido,
    }
