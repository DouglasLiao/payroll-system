# Fluxo e Lógica da Aplicação: Payroll System (Folha de Pagamento PJ)

Este documento mapeia todas as funcionalidades, fluxos e a lógica geral do sistema de folha de pagamento para colaboradores PJ (Pessoas Jurídicas).

## 1. Visão Geral

O sistema simplifica, automatiza e audita todo o processo de cálculo e pagamento de colaboradores B2B (PJ), desde o cadastro das empresas e prestadores de serviços até o envio dos comprovantes por e-mail e relatórios finais.

## 2. Atores do Sistema

- **Super Admin:** Tem acesso total à plataforma, gerencia empresas filiais, audita os pagamentos gerais e configurações do sistema.
- **Admin da Empresa (Company Admin):** Controla os colaboradores, modelos de cálculo e folhas apenas da sua respectiva empresa.
- **Colaborador / Prestador (Provider):** Pode eventualmente visualizar seus próprios recibos de pagamento ou histórico (caso habilitado no frontend).

## 3. Principais Features e Lógica

### 3.1. Gestão de Entidades

- **Gestão de Empresas (Companies):** Cadastro de múltiplas empresas (CNPJs) sob controle da mesma conta. Cada empresa pode ter regras customizadas de dias úteis (Ex: Comercial vs Fixo 30 dias).
- **Gestão de Prestadores (Providers):** Cadastro de contratos, honorários mensais (`monthly_value`), configuração de Vale Transporte (`vt_enabled`, `vt_fare`, `vt_trips_per_day`), e métodos de pagamento padrão.
- **Templates de Cálculo (Math Templates):** Criação de modelos reutilizáveis contendo regras e variáveis padrão que podem ser aplicadas às folhas, permitindo escalabilidade para times grandes.

### 3.2. Lógica de Cálculo da Folha (Payroll Engine)

O motor de cálculo (`CALCULOS_RESUMO_EXECUTIVO.md` / Engine) processa:

- **Salário Proporcional:** Baseado em faltas (Absences) e nos dias úteis definidos do mês (Workalendar vs 30 days rule).
- **Descontos Automáticos:** Faltas, Descontos manuais esporádicos.
- **Acréscimos Automáticos/Manuais:** Horas Extras (parametrizadas sob % acordado), Bônus, Vale Transporte.
- **Impostos e Taxas:** Cálculos de INSS/IRRF ou taxas de emissão de NF (caso parametrize retenções).
- _A lógica é unificada através de serviços robustos no Backend (Django), com forte cobertura de testes (Unitários e E2E) e Clean Architecture._

### 3.3. Ciclo de Vida da Folha de Pagamento (Flow)

1. **Configuração Mensal:** O Admin seleciona o mês/ano de referência.
2. **Geração / Aplicação do Template:** O sistema preenche automaticamente a folha para os prestadores com base no contrato (valor base).
3. **Lançamentos Variáveis:** O Admin lança as variáveis do mês para cada colaborador (inserção de Horas Extras, Faltas, etc.).
4. **Validação (Prévia):** Cálculos são simulados on-the-fly. O sistema mostra o valor Líquido a Pagar.
5. **Auditoria (Payroll Audit Agent):** O agente AI revisa os cálculos contra as políticas de pagamento para garantir zero anomalias.
6. **Aprovação e Pagamento:** O Admin aprova a folha. O status é alterado para "Paid".
7. **Disparo de Comunicação:** É enviada notificação (Email Service) com um recibo detalhado (PDF/HTML) ao prestador, confirmando o depósito.

### 3.4. Arquitetura

A infraestrutura utiliza uma abordagem Monolítica robusta ou separação lógica por domínios:

- **Backend (Django REST Framework):** Rotas separadas (Users API, Core/Site Manage, Auth). Utilização intensiva do padrão `Services/UseCases` e CQRS.
- **Frontend (React + Vite + TypeScript):** UI rica em componentes customizados (Material UI/Tailwind) e estado gerenciado via React Query.
- **Email Service:** Módulo/Serviço encarregado do envio de PDFs de fechamento aos provedores. Configurado com MailHog para testes.

## 4. Diferenciais do Produto (Value Proposition)

- **Eliminação de Erros Manuais:** Todo VT, falta e hora extra incide na base diária programada.
- **Multi-Tenancy Simplificado:** Perfeito para startups/agências com diversos CNPJs ou filiais.
- **Segurança e Log:** Todas as alterações no cadastro ou cálculos ficam logadas.
- **Velocidade de Gestão:** Com Templates e ações em massa, fecha-se a folha em minutos.
