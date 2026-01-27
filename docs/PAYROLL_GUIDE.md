# 📘 Guia do Sistema de Folha de Pagamento PJ

## Visão Geral

Este sistema gerencia o cálculo de pagamentos para prestadores **Pessoa Jurídica (PJ)** com regras contratuais customizadas que incluem conceitos atípicos para PJ, como horas extras, DSR e adicional noturno.

> **⚠️ ATENÇÃO:** Apesar de usar termos como "horas extras" e "DSR", este sistema é **EXCLUSIVAMENTE para PJ (Pessoa Jurídica)**. Esses conceitos não têm amparo legal trabalhista, sendo tratados apenas como **regras contratuais/comerciais** acordadas entre as partes. **NÃO implementa regras CLT**.

---

## 📋 Conceitos Fundamentais

### Regime de Trabalho

- **Tipo:** Pessoa Jurídica (PJ)
- **Sem vínculo CLT:** Não há INSS, FGTS, férias ou 13º obrigatórios
- **Pagamento:** Mensal com adiantamento quinzenal opcional
- **Regras:** Definidas por contrato comercial

### Componentes do Cálculo

#### **Proventos (Valores a Receber)**

1. Salário Base (após adiantamento)
2. Horas Extras 50%
3. Horas Trabalhadas em Feriados (100%)
4. DSR (Descanso Semanal Remunerado)
5. Adicional Noturno

#### **Descontos (Valores a Deduzir)**

1. Adiantamento Quinzenal
2. Atrasos
3. Faltas
4. Vale Transporte
5. Descontos Manuais

---

## 🧮 Fórmulas de Cálculo

### 1. Valor da Hora Contratual

```
valor_hora = valor_contrato_mensal ÷ carga_horaria_mensal
```

**Exemplo:**

- Salário: R$ 2.200,00
- Carga horária: 220 horas/mês
- **Valor/hora:** R$ 10,00

---

### 2. Adiantamento Quinzenal

```
valor_adiantamento = valor_contrato_mensal × percentual_adiantamento
saldo_pagamento = valor_contrato_mensal - valor_adiantamento
```

**Exemplo (40% de adiantamento):**

- Salário: R$ 2.200,00
- Adiantamento 40%: R$ 880,00
- **Saldo para final do mês:** R$ 1.320,00

---

### 3. Horas Extras (50% adicional)

```
valor_hora_extra_50 = valor_hora × 1.5
total_hora_extra_50 = horas_extras × valor_hora_extra_50
```

**Exemplo:**

- Valor/hora: R$ 10,00
- Valor hora extra: R$ 15,00
- Horas extras trabalhadas: 10 horas
- **Total hora extra:** R$ 150,00

---

### 4. Horas em Feriado (100% adicional)

```
valor_hora_feriado = valor_hora × 2.0
total_feriado = horas_feriado × valor_hora_feriado
```

**Exemplo:**

- Valor/hora: R$ 10,00
- Valor hora feriado: R$ 20,00
- Horas trabalhadas em feriado: 8 horas
- **Total feriado:** R$ 160,00

---

### 5. DSR (Descanso Semanal Remunerado)

O DSR é calculado sobre as horas extras E feriados trabalhados, proporcional aos dias úteis e domingos/feriados do mês.

**Fórmula:**

```
DSR = (Horas Extras + Feriados) / Dias Úteis * (Domingos + Feriados)
```

**Exemplo (Janeiro/2026 - 25 dias úteis, 6 domingos+feriados):**

- Total de horas extras: R$ 220,00
- Total de feriados: R$ 160,00
- Total extras: R$ 380,00
- DSR diário: 380 / 25 = R$ 15,20
- **DSR total: 15,20 \* 6 = R$ 91,20**

> [!IMPORTANT]
> O DSR varia a cada mês conforme o número de dias úteis e feriados.
> O sistema usa a biblioteca `workalendar` para calcular automaticamente
> os feriados brasileiros (nacionais e móveis como Carnaval e Páscoa).

---

### 6. Adicional Noturno (20%)

```
valor_hora_noturna = valor_hora × 0.20
adicional_noturno = horas_noturnas × valor_hora_noturna
```

**Exemplo:**

- Valor/hora: R$ 10,00
- Valor adicional noturno: R$ 2,00/hora
- Horas noturnas: 20 horas
- **Total adicional noturno:** R$ 40,00

---

### 7. Total de Proventos

```
total_proventos =
    saldo_pagamento +
    total_hora_extra_50 +
    total_feriado +
    dsr +
    adicional_noturno
```

**Exemplo completo (Janeiro/2026):**

```
Saldo após adiantamento: R$ 1.320,00
Horas extras 50%:        R$   150,00
Feriados trabalhados:    R$   160,00
DSR (310/25*6):          R$    74,40
Adicional noturno:       R$    40,00
─────────────────────────────────────
TOTAL PROVENTOS:         R$ 1.744,40
```

---

### 8. Descontos - Atrasos

```
desconto_atraso = (minutos_atraso ÷ 60) × valor_hora
```

**Exemplo:**

- Minutos de atraso: 30 minutos
- Valor/hora: R$ 10,00
- **Desconto:** R$ 5,00

---

### 9. Descontos - Faltas

```
desconto_falta = horas_falta × valor_hora
```

**Exemplo:**

- Horas de falta: 8 horas
- Valor/hora: R$ 10,00
- **Desconto:** R$ 80,00

---

### 10. Total de Descontos

> [!IMPORTANT] > **DSR sobre Faltas NÃO é aplicado** - Este é um conceito exclusivo de CLT.
> O sistema é **PJ-only** e não implementa regras trabalhistas CLT.

```
total_descontos =
    desconto_atraso +
    desconto_falta +
    vale_transporte +
    descontos_manuais
```

**Exemplo:**

```
Atrasos:                 R$   5,00
Faltas:                  R$  80,00
Vale transporte:         R$ 202,40
Descontos manuais:       R$   0,00
─────────────────────────────────────
TOTAL DESCONTOS:         R$ 287,40
```

---

### 11. Valor Líquido Final

```
valor_liquido_pagar = total_proventos - total_descontos
```

**Exemplo final:**

```
Total de Proventos:      R$ 1.695,00
Total de Descontos:      R$   287,40
─────────────────────────────────────
VALOR LÍQUIDO:           R$ 1.407,60 ✅
```

---

## 📊 Exemplo Completo (Caso Real)

### Dados de Entrada

- **Prestador:** João Silva
- **Salário Base:** R$ 2.200,00
- **Carga Horária:** 220 horas/mês
- **Adiantamento:** 40%
- **Horas extras 50%:** 10 horas
- **Horas feriado:** 8 horas
- **Horas noturnas:** 20 horas
- **Minutos de atraso:** 30 minutos
- **Horas de falta:** 8 horas
- **Vale transporte:** R$ 202,40

### Cálculos Passo a Passo

#### Passo 1: Valor da Hora

```
2.200 ÷ 220 = R$ 10,00/hora
```

#### Passo 2: Adiantamento

```
Adiantamento: 2.200 × 0.40 = R$ 880,00
Saldo: 2.200 - 880 = R$ 1.320,00
```

#### Passo 3: Proventos Variáveis (Janeiro/2026: 25 dias úteis, 6 dom+fer)

```
Hora extra (10h × 15):    R$ 150,00
Feriado (8h × 20):        R$ 160,00
DSR ((150+160)/25*6):     R$  74,40
Adicional noturno (20×2): R$  40,00
```

#### Passo 4: Descontos

```
Atrasos (30min):          R$   5,00
Faltas (8h):              R$  80,00
Vale transporte:          R$ 202,40
```

#### Passo 5: Totais

```
PROVENTOS:  1.320 + 150 + 160 + 74,40 + 40 = R$ 1.744,40
DESCONTOS:  5 + 80 + 202,40                = R$   287,40
LÍQUIDO:    1.744,40 - 287,40              = R$ 1.457,00 ✅
```

---

## 🔧 Configurações do Sistema

### Percentuais Padrão

- **Adiantamento quinzenal:** 40%
- **Hora extra:** 50% (multiplicador 1.5)
- **Feriado trabalhado:** 100% (multiplicador 2.0)
- **DSR:** Calculado dinamicamente por mês (varia conforme dias úteis e feriados)
- **Adicional noturno:** 20% (multiplicador 0.2)

### Carga Horária Padrão

- **Mensal:** 220 horas

### Vale Transporte

- Valor fixo por mês (ex: R$ 202,40)
- Descontado do valor líquido

---

## 📝 Fluxo de Trabalho

### 1. Cadastro de Prestador

- Nome completo
- Função/cargo
- Valor mensal do contrato
- Carga horária mensal
- Percentual de adiantamento
- Habilitar/desabilitar adiantamento
- Valor do vale transporte
- Dados bancários (PIX, conta, etc.)

### 2. Criação de Folha Mensal

- Selecionar prestador
- Informar mês de referência (MM/YYYY)
- Preencher dados variáveis:
  - Horas extras 50%
  - Horas em feriados
  - Horas noturnas
  - Minutos de atraso
  - Horas de falta
  - Descontos manuais
- Sistema calcula automaticamente:
  - Adiantamento
  - Valor/hora
  - Todos os proventos
  - Todos os descontos
  - Valor líquido final

### 3. Revisão e Fechamento

- Revisar todos os valores calculados
- Ver breakdown detalhado (itens)
- Adicionar observações (opcional)
- **Fechar folha** (impede edições)

### 4. Pagamento

- Marcar como **PAGO**
- Registrar data de pagamento
- Gerar recibo

### 5. Consulta e Relatórios

- Listar folhas por prestador
- Filtrar por mês, status
- Visualizar histórico
- Exportar dados

---

## 🎯 Status da Folha

### DRAFT (Rascunho)

- Folha recém-criada
- Pode ser editada e recalculada
- Valores podem mudar

### CLOSED (Fechada)

- Folha revisada e conferida
- Não pode mais ser editada
- Pronta para pagamento

### PAID (Paga)

- Pagamento realizado
- Data de pagamento registrada
- Histórico completo

---

## 🔐 Permissões Futuras

### Administrador

- ✅ Criar, editar, excluir prestadores
- ✅ Criar, recalcular, fechar folhas
- ✅ Marcar como pago
- ✅ Visualizar todas as folhas
- ✅ Gerar relatórios

### Prestador (Futuro)

- ✅ Visualizar apenas suas próprias folhas
- ✅ Consultar histórico de pagamentos
- ✅ Baixar recibos
- ❌ Não pode criar ou editar folhas

---

## 📐 Estrutura de Dados

### Provider (Prestador)

```python
{
  "id": 1,
  "name": "João Silva",
  "role": "Desenvolvedor",
  "monthly_value": 2200.00,
  "monthly_hours": 220,
  "advance_enabled": true,
  "advance_percentage": 40.00,
  "vt_value": 202.40,
  "payment_method": "PIX",
  "pix_key": "joao@email.com"
}
```

### Payroll (Folha de Pagamento)

```python
{
  "id": 1,
  "provider": 1,
  "reference_month": "01/2026",
  "base_value": 2200.00,
  "hourly_rate": 10.00,
  "advance_value": 880.00,
  "remaining_value": 1320.00,

  # Horas trabalhadas
  "overtime_hours_50": 10.0,
  "holiday_hours": 8.0,
  "night_hours": 20.0,

  # Descontos variáveis
  "late_minutes": 30,
  "absence_hours": 8.0,
  "manual_discounts": 0.00,
  "vt_discount": 202.40,

  # Proventos calculados
  "overtime_amount": 150.00,
  "holiday_amount": 160.00,
  "dsr_amount": 25.00,
  "night_shift_amount": 40.00,
  "total_earnings": 1695.00,

  # Descontos calculados
  "late_discount": 5.00,
  "absence_discount": 80.00,
  "total_discounts": 287.40,

  # Valores finais
  "gross_value": 1695.00,
  "net_value": 1457.00,

  # Status
  "status": "CLOSED",
  "notes": "Mês de janeiro completo",
  "closed_at": "2026-01-31T17:00:00Z",
  "paid_at": null
}
```

### PayrollItem (Itens Detalhados)

```python
[
  {"type": "CREDIT", "description": "Salário base (após adiantamento)", "amount": 1320.00},
  {"type": "CREDIT", "description": "Horas extras 50% (10h)", "amount": 150.00},
  {"type": "CREDIT", "description": "Feriados trabalhados (8h)", "amount": 160.00},
  {"type": "CREDIT", "description": "DSR sobre extras e feriados", "amount": 74.40},
  {"type": "CREDIT", "description": "Adicional noturno (20h)", "amount": 40.00},
  {"type": "DEBIT", "description": "Adiantamento quinzenal (40%)", "amount": 880.00},
  {"type": "DEBIT", "description": "Atrasos (30 minutos)", "amount": 5.00},
  {"type": "DEBIT", "description": "Faltas (8 horas)", "amount": 80.00},
  {"type": "DEBIT", "description": "Vale transporte", "amount": 202.40}
]
```

---

## 🚀 Endpoints da API

### Providers (Prestadores)

```
GET    /providers/           # Listar todos
POST   /providers/           # Criar novo
GET    /providers/{id}/      # Detalhe
PUT    /providers/{id}/      # Atualizar
DELETE /providers/{id}/      # Excluir
```

### Payrolls (Folhas)

```
GET    /payrolls/            # Listar todas
POST   /payrolls/create/     # Criar e calcular nova folha
GET    /payrolls/{id}/       # Detalhe com itens
PUT    /payrolls/{id}/       # Atualizar (apenas DRAFT)
POST   /payrolls/{id}/close/ # Fechar folha
POST   /payrolls/{id}/mark_paid/ # Marcar como pago

# Filtros
GET    /payrolls/?status=DRAFT
GET    /payrolls/?reference_month=01/2026
GET    /payrolls/?provider=1
```

---

## ⚡ Validações Importantes

### No Backend

- ✅ Horas extras >= 0
- ✅ Horas feriado >= 0
- ✅ Horas noturnas >= 0
- ✅ Minutos de atraso >= 0
- ✅ Horas de falta >= 0
- ✅ Adiantamento <= Salário base
- ✅ Mês de referência no formato MM/YYYY
- ✅ Não permitir edição de folhas CLOSED ou PAID
- ✅ Valores monetários sempre com 2 casas decimais

### No Frontend

- ✅ Validação em tempo real
- ✅ Formatação monetária (R$ 1.234,56)
- ✅ Mensagens de erro claras
- ✅ Confirmação antes de fechar/pagar folha

---

## 📚 Glossário

- **PJ:** Pessoa Jurídica
- **CLT:** Consolidação das Leis do Trabalho (não se aplica aqui)
- **DSR:** Descanso Semanal Remunerado (aqui usado como regra contratual)
- **VT:** Vale Transporte
- **Provento:** Valor a receber
- **Desconto:** Valor a deduzir
- **Salário Bruto:** Total de proventos
- **Salário Líquido:** Bruto menos descontos

---

## 📞 Suporte

Para dúvidas sobre cálculos ou funcionamento do sistema, consulte:

- Este guia (PAYROLL_GUIDE.md)
- Plano de implementação (implementation_plan.md)
- Código fonte em `backend/domain/payroll_calculator.py`

---

**Última atualização:** 15/01/2026
**Versão do guia:** 2.0 - DSR Corrigido (PJ-only)
