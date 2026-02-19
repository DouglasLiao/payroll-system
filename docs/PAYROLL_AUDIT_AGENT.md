# 🕵️ AGENT: Auditoria de Folha de Pagamento

Este documento serve como base para o AGENT responsável por ajustar o sistema de pagamentos conforme as regras definidas em `docs/CALCULOS_RESUMO_EXECUTIVO.md`.

## 🎯 Objetivo

Garantir que o código em `payroll-backend` reflita exatamente as regras de negócio acordadas na documentação executiva, corrigindo discrepâncias encontradas na lógica atual.

---

## 🔍 Diagnóstico de Discrepâncias

### 1. Desconto de Faltas (Absences) 🚨 **CRÍTICO**

- **Regra Documentada (Linha 128):**

  > "Novo desconto das faltas = (Salario Base) / (sempre 30) \* (numero de faltas)"
  - O cálculo deve ser baseado em **DIAS** de falta, usando um divisor fixo de 30.
  - Exemplo: `R$ 2.200 / 30 * 1 dia = R$ 73,33`.

- **Implementação Atual (`payroll_calculator.py`):**
  - O código principal (`calcular_folha_completa`) chama `calcular_desconto_falta(horas_falta, valor_hora)`.
  - Isso calcula baseado em **HORAS** (`8h * R$ 10 = R$ 80,00`), o que é **incorreto** segundo a nova regra.
  - Existe uma função `calcular_desconto_falta_por_dia` (Linha 503) que implementa a regra correta (1/30), mas ela **não está sendo usada** na função principal.

- **🛠️ Ação Necessária:**
  - Alterar `calcular_folha_completa` para receber `absence_days` (dias_falta) em vez de (ou além de) `absence_hours`.
  - Substituir a chamada de cálculo de desconto para usar `calcular_desconto_falta_por_dia`.
  - Atualizar `PayrollService` para passar `absence_days` corretamente.

---

### 2. Vale Transporte (VT) 🚨 **CRÍTICO**

- **Regra Documentada (Linhas 169, 189):**

  > "Desconto do vale transporte que faltou 1 dia... Pagamento feito separado."
  - O VT é pago separadamente (provavelmente cartão pré-pago).
  - Na folha, deve aparecer como **desconto apenas o valor não utilizado** (dias de falta).
  - Exemplo: Se faltou 1 dia, desconta-se o valor de 1 dia de VT (`viagens * tarifa`).
  - Total Descontos (Linha 171) soma `R$ 9,20` (o valor de 1 dia), **não** o valor cheio do mês.

- **Implementação Atual (`payroll_calculator.py`):**
  - A função `calcular_vale_transporte` calcula o VT baseado em **dias trabalhados** (`dias_uteis - faltas`).
  - O `PayrollService` adiciona esse valor calculado como um **DÉBITO** (Desconto) na folha.
  - **Resultado Atual:** O sistema está descontando o valor de todos os dias que a pessoa TRABALHOU. (Ex: Trabalhou 20 dias, desconta o VT de 20 dias). Isso anula o benefício se a intenção for apenas estornar o não-usado.

- **🛠️ Ação Necessária:**
  - Alterar a lógica para: `Desconto VT = Dias de Falta * Custo Diário do VT`.
  - Se a pessoa não faltou, o desconto de VT deve ser **ZERO** (assumindo que o benefício é pago à parte e não descontado do salário base).
  - Criar função `calcular_estorno_vt` em vez de `calcular_vale_transporte` atual.

---

### 3. DSR (Descanso Semanal Remunerado) ✅ **CORRETO**

- **Regra Documentada:**

  > `(Horas Extras + Feriados) / Dias Úteis * (Domingos + Feriados)`

- **Implementação Atual:**
  - `calcular_dsr` em `payroll_calculator.py` implementa exatamente esta fórmula.
  - A implementação está alinhada com a "Fórmula Nova (Correta)".

---

## 📝 Plano de Execução para o AGENT

### Passo 1: Atualizar Domínio (`payroll_calculator.py`)

1.  **Refatorar `calcular_folha_completa`:**
    - Adicionar argumento `dias_falta` (int).
    - **Faltas:** Alterar lógica para usar `calcular_desconto_falta_por_dia`.
    - **VT:** Alterar lógica para calcular desconto baseado em `dias_falta` (Estorno) em vez de `dias_trabalhados`.

### Passo 2: Atualizar Serviço (`payroll_service.py`)

1.  Garantir que `create_payroll` e `recalculate_payroll` passem `absence_days` corretamente para o calculador.
2.  Ajustar a criação dos itens (`_create_payroll_items`) para descrever corretamente o desconto de VT (ex: "Estorno VT por faltas" em vez de apenas "Vale transporte").

### Passo 3: Validação

1.  Executar testes existentes.
2.  Criar novo teste de caso de uso com o cenário do documento:
    - Salário: 2.200,00
    - Faltas: 1 dia (8h)
    - **Verificar:** Desconto Falta deve ser `73,33` (não 80,00).
    - **Verificar:** Desconto VT deve ser referente a 1 dia apenas (ex: `9,20`).

---

## 🧪 Casos de Teste (Exemplo Doc)

| Item                | Valor Atual (Código)               | Valor Esperado (Doc)     | Status     |
| ------------------- | ---------------------------------- | ------------------------ | ---------- |
| **Salário Base**    | R$ 1.320,00 (pós adiantamento 40%) | R$ 1.320,00              | ✅ OK      |
| **Desconto Atraso** | R$ 5,00 (30 min)                   | R$ 5,00                  | ✅ OK      |
| **Desconto Falta**  | R$ 80,00 (8h \* 10,00)             | **R$ 73,33** (1/30)      | ❌ AJUSTAR |
| **Desconto VT**     | ~R$ 380,00 (dias trab)             | **R$ 9,20** (dias falta) | ❌ AJUSTAR |
