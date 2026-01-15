# 💰 Cálculos da Folha de Pagamento PJ

## Valores Base

```
Valor Contratual:     R$ 2.200,00
Carga Horária:        220 horas/mês
Valor/Hora:           R$ 10,00
Adiantamento (40%):   R$ 880,00
```

---

## PROVENTOS

### 1. Salário Base

```
Saldo = R$ 2.200,00 - R$ 880,00 = R$ 1.320,00
```

### 2. Horas Extras (50%)

```
HE = 10h × R$ 10,00 × 1.5 = R$ 150,00
```

### 3. Feriados (100%)

```
Feriado = 8h × R$ 10,00 × 2.0 = R$ 160,00
```

### 4. DSR (Dinâmico)

```
DSR = (HE + Feriado) / Dias Úteis × (Domingos + Feriados)
    = (R$ 150 + R$ 160) / 25 × 6
    = R$ 310 / 25 × 6
    = R$ 12,40 × 6
    = R$ 74,40
```

### 5. Adicional Noturno (20%)

```
Noturno = 20h × R$ 10,00 × 0.20 = R$ 40,00
```

### Total Proventos

```
R$ 1.320,00 + R$ 150,00 + R$ 160,00 + R$ 74,40 + R$ 40,00 = R$ 1.744,40
```

---

## DESCONTOS

### 1. Adiantamento

```
R$ 880,00
```

### 2. Atrasos

```
30min / 60 × R$ 10,00 = R$ 5,00
```

### 3. Faltas

```
8h × R$ 10,00 = R$ 80,00
```

### 4. Vale Transporte

```
R$ 202,40
```

### Total Descontos

```
R$ 880,00 + R$ 5,00 + R$ 80,00 + R$ 202,40 = R$ 1.167,40
```

---

## VALOR LÍQUIDO

```
Total Proventos  - Total Descontos = Valor Líquido
R$ 1.744,40      - R$ 1.167,40     = R$ 577,00
```

---

## Comparação DSR (Antes vs Depois)

| Cálculo        | Antes       | Depois         |
| -------------- | ----------- | -------------- |
| **Fórmula**    | HE × 16,67% | (HE+Fer)/DU×DF |
| **HE**         | R$ 150,00   | R$ 150,00      |
| **Feriado**    | R$ 0,00     | R$ 160,00      |
| **Dias Úteis** | -           | 25             |
| **Dom+Fer**    | -           | 6              |
| **DSR**        | R$ 25,00    | **R$ 74,40**   |
| **Diferença**  | -           | **+R$ 49,40**  |

---

## Calendário Mensal (Exemplos)

### Janeiro/2026

- Dias: 31 | Úteis: 25 | Dom+Fer: 6
- DSR mais alto (menos dias úteis)

### Fevereiro/2026

- Dias: 28 | Úteis: 20 | Dom+Fer: 8
- DSR médio

### Dezembro/2026

- Dias: 31 | Úteis: 22 | Dom+Fer: 9
- DSR mais alto (Natal)

---

**Legenda:**

- HE = Horas Extras
- Fer = Feriados
- DU = Dias Úteis
- DF = Domingos + Feriados
- DSR = Descanso Semanal Remunerado
