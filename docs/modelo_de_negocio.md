# 📑 Modelo de Negócio – Cálculo de Pagamento PJ

Este documento descreve **exclusivamente** as regras de cálculo utilizadas para pagamento de **Prestadores de Serviço (PJ)**.
Não há vínculo CLT. Todos os itens abaixo representam **regras contratuais**.

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

### 1. Salário Base (Saldo)

```
Saldo = Valor Mensal - Adiantamento
      = 2.200,00 - 880,00
      = R$ 1.320,00
```

---

### 2. Horas Extras (50%)

```
Valor Hora Extra = Horas × Valor/Hora × 1.5
```

**Exemplo**

```
10h × 10,00 × 1.5 = R$ 150,00
```

---

### 3. Feriados Trabalhados (100%)

```
Valor Feriado = Horas × Valor/Hora × 2.0
```

**Exemplo**

```
8h × 10,00 × 2.0 = R$ 160,00
```

---

### 4. DSR – Descanso Semanal Remunerado (Regra Contratual)

```
DSR = (Valor Horas Extras + Valor Feriados)
      ÷ Dias Úteis
      × (Domingos + Feriados)
```

**Exemplo**

```
Horas Extras:        R$ 150,00
Feriados:            R$ 160,00
Total Base:          R$ 310,00
Dias Úteis:          25
Domingos/Feriados:   5

DSR = 310 ÷ 25 × 5 = R$ 73,81
```

---

### 5. Adicional Noturno (20%)

```
Valor Noturno = Horas × Valor/Hora × 1.20
```

**Exemplo**

```
20h × 10,00 × 1.20 = R$ 240,00
```

---

### 📊 Total de Proventos

```
Salário Base:        R$ 1.320,00
Horas Extras:        R$   150,00
Feriados:            R$   160,00
DSR:                 R$    73,81
Adicional Noturno:   R$   240,00
━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL PROVENTOS:     R$ 1.943,81
```

---

## 📉 DESCONTOS (Valores a Deduzir)

### 1. Atrasos

```
Desconto = (Minutos ÷ 60) × Valor/Hora
```

**Exemplo**

```
30 min ÷ 60 × 10,00 = R$ 5,00
```

---

### 2. Faltas (Regra Atualizada)

```
Desconto Falta = Salário Contratual ÷ 30 × Nº de Faltas
```

**Exemplo**

```
2.200,00 ÷ 30 = 73,33 por dia
1 falta = R$ 73,33
```

---

### 3. Vale Transporte (Cálculo Separado)

```
Valor Diário = Nº de passagens × Valor da passagem
```

**Exemplo – Belém**

```
Passagem: R$ 4,60
Ida e Volta: 2 passagens
Valor Diário: 9,20
```

```
Dias Trabalhados = Dias úteis - Faltas
Desconto VT = Dias Trabalhados × Valor Diário
```

**Exemplo**

```
19 dias × 9,20 = R$ 174,80
```

⚠️ O vale transporte **não entra no líquido principal**, é tratado em **página/cálculo separado**.

---

### 📊 Total de Descontos (Exemplo sem VT)

```
Atrasos:             R$  5,00
Faltas:              R$ 73,33
Desconto VT Falta:   R$  9,20
━━━━━━━━━━━━━━━━━━━━━━━━━━
TOTAL DESCONTOS:     R$ 87,53
```

---

## 💵 VALOR LÍQUIDO FINAL

```
Total Proventos:     R$ 1.943,81
(-) Descontos:       R$    87,53
━━━━━━━━━━━━━━━━━━━━━━━━━━
VALOR A PAGAR:       R$ 1.856,28
```

---

## 🧠 Observações para Implementação no Sistema

- Todos os cálculos são **contratuais (PJ)**
- Nenhuma regra CLT se aplica
- DSR varia conforme calendário mensal
- Vale Transporte deve ter:
  - Página própria
  - Cálculo independente
  - Integração apenas informativa no resumo

---

Documento pronto para:

- Validação financeira
- Apresentação técnica
- Implementação em Django + React
