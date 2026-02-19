# 📊 Sistema de Folha PJ - Resumo de Cálculos

> **Apresentação Stakeholders | Janeiro 2026**

---

## 🎯 Visão Geral

Sistema automatizado para cálculo de folha de pagamento de **prestadores PJ** com regras contratuais customizadas.

### Características:

- ✅ 100% automatizado - zero cálculos manuais
- ✅ Transparente - cada centavo detalhado
- ✅ Flexível - adapta-se ao calendário mensal
- ✅ Preciso - usa feriados oficiais brasileiros

---

## 💰 Estrutura de Pagamento

### Valores Base

```
Valor Contratual Mensal:  R$ 2.200,00
Carga Horária Mensal:     220 horas
├─ Valor/Hora:            R$ 10,00
└─ Adiantamento (40%):    R$ 880,00
   Saldo Final Mês:       R$ 1.320,00
```

---

## 📈 PROVENTOS (Valores a Receber)

### 1. Salário Base

```
Saldo = Valor Mensal - Adiantamento
      = R$ 2.200,00 - R$ 880,00
      = R$ 1.320,00

      //valor da hora é 10 reais
```

### 2. Horas Extras (50% adicional)

```
Valor HE = Horas × Valor/Hora × 1.5
         = 10h × R$ 10,00 × 1.5
         = R$ 150,00
```

### 3. Feriados Trabalhados (100% adicional)

```
Valor Feriado = Horas × Valor/Hora × 2.0
              = 8h × R$ 10,00 × 2.0
              = R$ 160,00
```

### 4. DSR - Descanso Semanal Remunerado ⭐ ATUALIZADO

```
Fórmula Nova (correta):
DSR = (Horas Extras + Feriados) / Dias Úteis × (Domingos + Feriados)

Exemplo Janeiro/2026:
├─ Horas Extras:        R$ 150,00
├─ Feriados:            R$ 160,00
├─ Total:               R$ 310,00
├─ Dias Úteis:          25
├─ Domingos+Feriados:   5
│
└─ DSR = 310 / 25 × 5 = R$ 73,81
```

> **💡 Diferença:** DSR varia conforme o calendário mensal automaticamente

### 5. Adicional Noturno (20%)

```
Valor Noturno = Horas × Valor/Hora × 1.20
              = 20h × R$ 10,00 × 1.20
              = R$ 240,00
```

### 📊 Total de Proventos

```
Salário Base:          R$ 1.320,00
+ Horas Extras 50%:    R$   150,00
+ Feriados:            R$   160,00
+ DSR:                 R$    74,40
+ Adicional Noturno:   R$   240,00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL PROVENTOS:       R$ 2.034,40
```

// 1944,40

---

## 📉 DESCONTOS (Valores a Deduzir)

### 1. Adiantamento Quinzenal

```
Já pago no meio do mês:  R$ 880,00
```

### 2. Atrasos

```
Desconto = (Minutos / 60) × Valor/Hora
         = (30 / 60) × R$ 10,00
         = R$ 5,00
```

### 3. Faltas

```
Desconto = Horas × Valor/Hora
         = 8h × R$ 10,00
         = R$ 80,00
```

Novo desconto das faltas = (Salario Base) / (sempre 30) \* (numero de faltas)
eg: 1 dia /30 = 73,33

2.200,00/30 = 73,33

### 4. Vale Transporte

```
Valor fixo mensal:       R$ 202,40
```

Calculados no dia do mês trabalhados no mês
4,60 em Belem

2 onibus _ passagem _ dias que ele foi para o trabalho.

184,00

---

4 onibus (ida e volta) \* dias que ele foi para o trabalho
368,00

20 dias.

Tambeḿ é considerado o dia que ele vai para o escritorio.

ex.
ele foi 20 dias para o escritorio. (na teoria)
mas ele faltou 1 dia

então é 19\* a passagem

EnTão é descontado no final do mês.

### 📊 Total de Descontos

```
<!-- Adiantamento:          R$   880,00 -->
+ Atrasos:             R$     5,00
+ Faltas (Linkar com o vale trasporte):              R$    73,33
+ Desconto do vale transporte que faltou 1 dia 4,60*2 = 9,20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL DESCONTOS:       R$ 87,53

```

## <!-- + Vale Transporte:     R$   19*4,60*2 = 174,80 -->

## 💵 VALOR LÍQUIDO FINAL

```
┌─────────────────────────────────────┐
│  CÁLCULO DO PAGAMENTO FINAL         │
├─────────────────────────────────────┤
│  Total Proventos:    R$ 1944,40     │
│  (-) Total Descontos: R$ 87,53      │
│  ═══════════════════════════════════│
│  VALOR A PAGAR:     R$   1.856,87 ✅│
└─────────────────────────────────────┘

Vale transporte fazer uma nova parte do cálculo. Pois o pagamento é feito separado.
Nova pagina também. // Pagina do vale transporte
// Corrigir.


```

> **Observação:** Adiantamento de R$ 880,00 já foi pago anteriormente

---

## 🔄 Correção Implementada - DSR

### ❌ Fórmula Antiga (Incorreta)

```
DSR = Horas Extras × 16,67%
    = R$ 150,00 × 0.1667
    = R$ 25,00
```

- Percentual fixo (não considerava calendário)
- Não incluía feriados trabalhados
- Incluía "DSR sobre faltas" (conceito CLT)

### ✅ Fórmula Nova (Correta)

```
DSR = (Horas Extras + Feriados) / Dias Úteis × (Domingos + Feriados)
    = (R$ 150 + R$ 160) / 25 × 6
    = R$ 74,40
```

- Dinâmica (adapta-se ao mês)
- Inclui feriados trabalhados
- Sistema PJ-only (sem conceitos CLT)
- Usa calendário oficial brasileiro

### 📊 Impacto Financeiro

| Item              | Antes     | Depois    | Diferença     |
| ----------------- | --------- | --------- | ------------- |
| DSR               | R$ 25,00  | R$ 74,40  | **+R$ 49,40** |
| DSR s/ Faltas     | R$ 13,33  | R$ 0,00   | **-R$ 13,33** |
| **Total Líquido** | R$ 540,67 | R$ 577,00 | **+R$ 36,33** |

> **✅ Benefício:** Cálculo mais justo e correto conforme acordado contratualmente

---

## 🗓️ Calendário Automático

Sistema calcula automaticamente para cada mês:

### Janeiro/2026

- 31 dias no mês
- 25 dias úteis
- 6 domingos + feriados
- **DSR: Maior** (menos dias úteis = mais DSR)

### Fevereiro/2026

- 28 dias no mês
- ~20 dias úteis
- 8 domingos + feriados
- **DSR: Similar**

### Dezembro/2026

- 31 dias no mês
- ~22 dias úteis (Natal)
- 9 domingos + feriados
- **DSR: Maior** (mais domingos/feriados)

---

## ✨ Feriados Brasileiros (Automáticos)

### Fixos

- 01/01 - Ano Novo
- 21/04 - Tiradentes
- 01/05 - Trabalho
- 07/09 - Independência
- 12/10 - N. Sra. Aparecida
- 02/11 - Finados
- 15/11 - Proclamação
- 25/12 - Natal

### Móveis (calculados)

- Carnaval
- Sexta-feira Santa
- Páscoa
- Corpus Christi

> **Tecnologia:** Biblioteca `workalendar` - atualizada automaticamente

---

## 📋 Exemplo Completo - Passo a Passo

### Entrada de Dados

```
Prestador:           João Silva
Mês Referência:      Janeiro/2026
Salário Contratual:  R$ 2.200,00
Horas Extras:        10 horas
Feriados:            8 horas
Horas Noturnas:      20 horas
Atrasos:             30 minutos
Faltas:              8 horas
Vale Transporte:     R$ 202,40
```

### Processamento Automático

```
1. Sistema busca calendário de Jan/2026
   └─ 25 dias úteis, 6 domingos+feriados

2. Calcula valor/hora
   └─ R$ 2.200 / 220h = R$ 10,00/h

3. Calcula todos os proventos
   ├─ Saldo: R$ 1.320,00
   ├─ HE 50%: R$ 150,00
   ├─ Feriados: R$ 160,00
   ├─ DSR: R$ 74,40
   └─ Noturno: R$ 40,00

4. Calcula todos os descontos
   ├─ Adiantamento: R$ 880,00
   ├─ Atrasos: R$ 5,00
   ├─ Faltas: R$ 80,00
   └─ VT: R$ 202,40

5. Valor final
   └─ R$ 1.744,40 - R$ 1.167,40 = R$ 577,00
```

### Saída - Recibo Detalhado

```
═══════════════════════════════════════════════════════
           FOLHA DE PAGAMENTO - JANEIRO/2026
═══════════════════════════════════════════════════════

PRESTADOR: João Silva
MÊS: Janeiro/2026

PROVENTOS:
  Salário base (após adiantamento)      R$ 1.320,00
  Horas extras 50% (10h)                R$   150,00
  Feriados trabalhados (8h)             R$   160,00
  DSR sobre extras e feriados           R$    74,40
  Adicional noturno (20h)               R$    40,00
                                      ─────────────
  TOTAL PROVENTOS                       R$ 1.744,40

DESCONTOS:
  Adiantamento quinzenal (40%)          R$   880,00
  Atrasos (30 minutos)                  R$     5,00
  Faltas (8 horas)                      R$    80,00
  Vale transporte                       R$   202,40
                                      ─────────────
  TOTAL DESCONTOS                       R$ 1.167,40

═══════════════════════════════════════════════════════
VALOR LÍQUIDO A PAGAR                   R$   577,00
═══════════════════════════════════════════════════════

Adiantamento de R$ 880,00 já pago em 15/01/2026
```

---

## 🎯 Benefícios do Sistema

### Precisão

- ✅ Cálculos automáticos (zero erro humano)
- ✅ Fórmulas validadas
- ✅ Arredondamento correto (2 casas decimais)

### Transparência

- ✅ Cada valor detalhado
- ✅ Histórico completo
- ✅ Auditável

### Conformidade

- ✅ Regras contratuais PJ
- ✅ Calendário brasileiro oficial
- ✅ Documentação completa

### Eficiência

- ✅ Processamento em segundos
- ✅ Recálculo instantâneo
- ✅ Sem trabalho manual

---

## 📞 Informações Técnicas

**Sistema:** Folha de Pagamento PJ  
**Tipo de Contrato:** Pessoa Jurídica (sem vínculo CLT)  
**Versão:** 2.0 - DSR Corrigido  
**Data:** Janeiro 2026  
**Status:** ✅ Operacional

---

**Preparado para:** Apresentação Stakeholders  
**Data:** 15/01/2026
