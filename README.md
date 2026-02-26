# Fluxo, Lógica e Arquitetura: Payroll System (Folha de Pagamento PJ)

Este documento mapeia todas as funcionalidades, fluxos e a lógica geral do sistema de folha de pagamento para colaboradores PJ (Pessoas Jurídicas), bem como o detalhamento arquitetural da aplicação.

---

## 1. Visão Geral Arquitetural (Monorepo)

O repositório adota uma abordagem de **Monorepo** muito organizada, dividida em quatro pilares principais, que isola as responsabilidades de backend, frontends (aplicação e landing page) e estilização global:

- `payroll-backend`
- `payroll-frontend`
- `payroll-landing-page`
- `payroll-design-system`

## 2. Backend (Django REST Framework)

O backend destaca-se pela excelente organização e adoção de práticas modernas em engenharia de software, fugindo do padrão MVC tradicional do Django ("Fat Models, Fat Views") e partindo para um modelo escalável.

### 2.1 Padrão Arquitetural: Clean Architecture & Domain-Driven Design (DDD)

Dentro dos principais bounded contexts (módulos como `site_manage` e `users`), foi identificada a estruturação através da Clean Architecture, dividida rigorosamente nas seguintes camadas:

- **`api/`**: A camada de apresentação (Controllers). Onde residem as `views.py`, `urls.py` e `serializers.py`. Seu único papel é expor os endpoints e tratar a ponte HTTP.
- **`application/`**: O coração da coordenação. Aqui reside a orquestração de regras de negócio complexas. Notável a divisão interna em CQRS (Command Query Responsibility Segregation) com as pastas `commands/` e `queries/`, e os services utilitários (Emails, CSV).
- **`domain/`**: A lógica pura do negócio, independente de banco de dados ou frameworks. Onde se encontram agentes como o `payroll_calculator.py`.
- **`infrastructure/`**: Onde os `models.py` (banco de dados) efetivamente residem. Essa camada implementa os detalhes técnicos (persistência e mapeamento ORM).

## 3. Frontend (React + Vite + TypeScript)

O frontend também reflete um design muito bem pensado, voltado tanto para a manutenção rápida quanto para a segurança no tráfego de dados e UI consistente.

### 3.1 Padrão de Estado do Cliente vs. Servidor

- **Server State**: Toda a comunicação e gerenciamento de estado das requisições com a API são extraídas via **React Query (`@tanstack/react-query`)**. Isso delega as pesadas lógicas de cache, loaders, retries e revalidação (`invalidateQueries`) para a biblioteca, despoluindo os componentes.
- **Client State/Global**: O estado do cliente global utiliza nativamente a Context API do React (`AuthContext` e `ThemeContext`), o que é suficiente e ideal sem colocar bibliotecas de store massivas (como Redux) excessivas.

### 3.2 Estruturação de UI e Consistência (Design System Central)

- O projeto usa como fundação a extração da inteligência de UI e Tema através do pacote `@payroll/design-system`.
- Ao isolar os temas, o `payroll-frontend` e a `payroll-landing-page` conversam em sintonia, limitando discrepâncias visuais, uma das maiores armadilhas de sistemas que possuem "duas caras" (app e LP). Tudo isso foi envelopado via **Material UI (MUI)** modificado, entregando consistência no ecossistema inteiro.

### 3.3 Roteamento Baseado em Funções (Role-Based Access Control)

As rotas do sistema (`App.tsx`) delegam claramente o componente `ProtectedRoute` para tratar restrições no nível da interface. A separação entre ambientes de Super Admin, Customer Admin e Provider através de hierarquia de pastas nas `pages/` garante uma manutenção direta para cada persona do produto.

### 3.4 Padrão de Integração Analítica e Tipada (Services / Axios)

Os serviços em `src/services/` usam instâncias separadas por entidades (`dashboardApi.ts`, `superAdminApi.ts`). Isso modulariza totalmente as conexões de API com a base e garante que os contratos do TypeScript atuem diretamente nesse ponto.

---

## 4. Atores do Sistema

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
