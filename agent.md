# 🔍 Revisão de Estrutura e Cálculos do Sistema de Folha de Pagamento PJ

## 📋 Objetivo

Este documento serve como guia para revisar e validar a implementação dos cálculos de folha de pagamento para **Prestadores de Serviço (PJ)** conforme as regras definidas no [modelo_de_negocio.md](file:///home/douglasliao/Estudos/payroll-system/docs/modelo_de_negocio.md).

---

## Antes da revisão:

O sistema tem um fluxo de login com user e password.
Deixe memorizado se caso precisar realizar algum teste com login.
User: admin@techsolutions.com
Password: password123

Seja pragmatico, pontual e objetivo. Procure fazer os calculos de forma precisa e correta.

## ✅ Checklist de Validação

### 1. **Valores Base para exemplo**

- [ ] Valor Contratual Mensal: R$ 2.200,00
- [ ] Carga Horária Mensal: 220 horas
- [ ] Valor/Hora calculado: R$ 10,00
- [ ] Adiantamento (40%): R$ 880,00
- [ ] Saldo Base: R$ 1.320,00

**Verificar em:**

- Backend: Models e cálculos relacionados
- Frontend: Formulários de entrada e exibição

---

### 2. **PROVENTOS - Cálculos de Valores a Receber**

#### 2.1 Salário Base (Saldo)

```
Saldo = Valor Mensal - Adiantamento
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 2.200,00 - 880,00 = R$ 1.320,00

#### 2.2 Horas Extras (50%)

```
Valor Hora Extra = Horas × Valor/Hora × 1.5
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 10h × 10,00 × 1.5 = R$ 150,00

#### 2.3 Feriados Trabalhados (100%)

```
Valor Feriado = Horas × Valor/Hora × 2.0
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 8h × 10,00 × 2.0 = R$ 160,00

#### 2.4 DSR (Descanso Semanal Remunerado)

```
DSR = (Valor Horas Extras + Valor Feriados) ÷ Dias Úteis × (Domingos + Feriados)
```

- [ ] Fórmula implementada corretamente
- [ ] Calendário dinâmico implementado (dias úteis, domingos, feriados)
- [ ] Teste: (150,00 + 160,00) ÷ 25 × 5 = R$ 73,81
- [ ] Verificar se está usando `calendarUtils.ts`

#### 2.5 Adicional Noturno (20%)

```
Valor Noturno = Horas × Valor/Hora × 1.20
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 20h × 10,00 × 1.20 = R$ 240,00

#### 2.6 Total de Proventos

- [ ] Somatória correta de todos os proventos
- [ ] Teste: 1.320,00 + 150,00 + 160,00 + 73,81 + 240,00 = R$ 1.943,81

---

### 3. **DESCONTOS - Cálculos de Valores a Deduzir**

#### 3.1 Atrasos

```
Desconto = (Minutos ÷ 60) × Valor/Hora
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 30 min ÷ 60 × 10,00 = R$ 5,00

#### 3.2 Faltas

```
Desconto Falta = Salário Contratual ÷ 30 × Nº de Faltas
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 2.200,00 ÷ 30 × 1 = R$ 73,33

#### 3.3 Vale Transporte (VT)

```
Valor Diário = Nº de passagens × Valor da passagem
Dias Trabalhados = Dias úteis - Faltas
Desconto VT = Dias Trabalhados × Valor Diário
```

- [ ] Cálculo separado do líquido principal
- [ ] Página/componente próprio para VT
- [ ] Teste: 19 dias × 9,20 = R$ 174,80
- [ ] VT **NÃO** entra no valor líquido principal

#### 3.4 Total de Descontos (sem VT)

- [ ] Somatória correta dos descontos (atrasos + faltas)
- [ ] Teste: 5,00 + 73,33 = R$ 78,33

---

### 4. **VALOR LÍQUIDO FINAL**

```
Valor Líquido = Total Proventos - Total Descontos
```

- [ ] Fórmula implementada corretamente
- [ ] Teste: 1.943,81 - 78,33 = R$ 1.865,48
- [ ] **VT não deve estar incluído neste cálculo**

---

## 🔎 Áreas do Código para Revisar

### Backend (Django)

1. **Models:**
   - [ ] `Payroll` model
   - [ ] `Provider` model
   - [ ] Campos relacionados a horas, descontos, proventos

2. **Cálculos:**
   - [ ] Função de cálculo de proventos
   - [ ] Função de cálculo de descontos
   - [ ] Lógica de DSR
   - [ ] Cálculo de VT separado

3. **Endpoints:**
   - [ ] `/payrolls/calculate/`
   - [ ] Endpoints relacionados a VT

### Frontend (React)

1. **Componentes:**
   - [ ] `PayrollFormDialog.tsx`
   - [ ] Campos de entrada de dados
   - [ ] Exibição de cálculos

2. **Utilities:**
   - [ ] `calendarUtils.ts` (DSR dinâmico)
   - [ ] Funções auxiliares de cálculo

3. **Páginas de VT:**
   - [ ] Verificar se existe componente separado para VT
   - [ ] Verificar integração com o resumo

---

## 🧪 Testes de Validação

### Caso de Teste 1: Cenário Completo

```
Entrada:
- Valor Contratual: R$ 2.200,00
- Adiantamento: R$ 880,00
- Horas Extras (50%): 10h
- Feriados: 8h
- Adicional Noturno: 20h
- Atrasos: 30 min
- Faltas: 1 dia
- Dias Úteis: 25
- Domingos + Feriados: 5

Resultado Esperado:
- Salário Base: R$ 1.320,00
- Horas Extras: R$ 150,00
- Feriados: R$ 160,00
- DSR: R$ 62,00
- Adicional Noturno: R$ 240,00
- Total Proventos: R$ 1.943,81
- Atrasos: -R$ 5,00
- Faltas: -R$ 73,33
- Total Descontos: R$ 78,33
- VALOR LÍQUIDO: R$ 1.865,48
```

### Caso de Teste 2: Apenas Salário Base

```
Entrada:
- Valor Contratual: R$ 2.200,00
- Adiantamento: R$ 880,00
- Sem extras, feriados, noturno, atrasos ou faltas

Resultado Esperado:
- Salário Base: R$ 1.320,00
- VALOR LÍQUIDO: R$ 1.320,00
```

### Caso de Teste 3: Vale Transporte

```
Entrada:
- Passagem: R$ 4,60
- Ida e Volta: 2 passagens
- Dias Úteis: 20
- Faltas: 1 dia

Resultado Esperado:
- Valor Diário VT: R$ 9,20
- Dias Trabalhados: 19
- Total VT: R$ 174,80
- Este valor NÃO deve aparecer no líquido principal
```

---

## 📝 Notas Importantes

1. **Todos os cálculos são contratuais (PJ)**, não CLT
2. **DSR varia conforme calendário mensal** - implementação dinâmica necessária
3. **Vale Transporte:**
   - Deve ter página/cálculo separado
   - NÃO entra no valor líquido principal
   - Integração apenas informativa no resumo

---

## 🎯 Próximos Passos

1. [ ] Revisar o código backend (models e cálculos)
2. [ ] Revisar o código frontend (componentes e utils)
3. [ ] Executar testes de validação
4. [ ] Corrigir discrepâncias encontradas
5. [ ] Documentar mudanças necessárias
6. [ ] Implementar correções
7. [ ] Validar com casos de teste reais

---

**Data de Criação:** 2026-02-04  
**Referência:** [modelo_de_negocio.md](file:///home/douglasliao/Estudos/payroll-system/docs/modelo_de_negocio.md)
