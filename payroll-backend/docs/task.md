# Task: Melhorias no Dashboard - API e Filtros

## 🎯 Objetivo Geral

Implementar sistema completo de filtros e otimizações no dashboard do sistema de payroll, incluindo melhorias no backend (Django) e frontend (React/TypeScript).

---

## 📋 Fase 1: Fundamentos (Prioridade Alta) 🔴

### Backend - Expandir Endpoint Dashboard

- [ ] **1.1. Adicionar suporte a query parameters**
  - [ ] Implementar filtro `start_date` (data inicial)
  - [ ] Implementar filtro `end_date` (data final)
  - [ ] Implementar filtro `provider_id` (filtrar por prestador)
  - [ ] Implementar filtro `status` (DRAFT/CLOSED/PAID)
  - [ ] Implementar filtro `reference_month` (mês MM/YYYY)

- [ ] **1.2. Criar método auxiliar de filtros**
  - [ ] Implementar `get_filtered_payrolls()` em `ProtectedDashboardView`
  - [ ] Validar parâmetros de entrada
  - [ ] Aplicar filtros ao queryset

- [ ] **1.3. Adicionar agregação mensal**
  - [ ] Implementar `get_monthly_data()` para agrupar por mês
  - [ ] Calcular totais por mês (count, valores)
  - [ ] Calcular valores por status (draft_value, closed_value, paid_value)

- [ ] **1.4. Adicionar top providers**
  - [ ] Implementar `get_top_providers()` com limit de 5
  - [ ] Agregar total de payrolls por provider
  - [ ] Agregar valores totais e médios

- [ ] **1.5. Atualizar response do endpoint**
  - [ ] Adicionar campos `draft_value`, `closed_value`, `paid_value` em stats
  - [ ] Adicionar campo `avg_payroll_value` em stats
  - [ ] Adicionar campo `monthly_data` ao response
  - [ ] Adicionar campo `top_providers` ao response
  - [ ] Adicionar campo `filters_applied` ao response

### Frontend - Refatoração e Novos Componentes

- [ ] **1.6. Atualizar Types**
  - [ ] Criar interface `DashboardFilters` em `types/index.ts`
  - [ ] Atualizar interface `DashboardStats` com novos campos
  - [ ] Adicionar tipos para `monthly_data`
  - [ ] Adicionar tipos para `top_providers`

- [ ] **1.7. Atualizar API Service**
  - [ ] Modificar `getDashboardStats()` para aceitar filtros
  - [ ] Implementar construção de query params
  - [ ] Atualizar tipagem do response

- [ ] **1.8. Refatorar Hook useDashboardData**
  - [ ] Adicionar state para `filters`
  - [ ] Implementar função `setFilters`
  - [ ] Passar filtros para `getDashboardStats`
  - [ ] Adicionar cache com `staleTime` de 5 minutos
  - [ ] Remover requisições redundantes (buscar apenas dashboard)

- [ ] **1.9. Criar Componente DashboardFilters**
  - [ ] Criar arquivo `src/components/dashboard/DashboardFilters.tsx`
  - [ ] Implementar DatePicker para período (start/end date)
  - [ ] Implementar Autocomplete para provider
  - [ ] Implementar Select para status
  - [ ] Implementar TextField para mês de referência
  - [ ] Adicionar botão "Aplicar Filtros"
  - [ ] Adicionar botão "Limpar Filtros"

- [ ] **1.10. Atualizar Dashboard Page**
  - [ ] Importar e usar `DashboardFilters`
  - [ ] Conectar filtros ao hook
  - [ ] Passar dados diretamente do backend (sem cálculos locais)
  - [ ] Atualizar componentes para usar novos dados

### Testes e Validação

- [ ] **1.11. Testes Backend**
  - [ ] Testar filtros individuais (start_date, end_date, etc)
  - [ ] Testar combinação de filtros
  - [ ] Testar agregação mensal
  - [ ] Testar top providers
  - [ ] Testar permissões (Customer Admin only)

- [ ] **1.12. Testes Frontend**
  - [ ] Testar componente DashboardFilters
  - [ ] Testar aplicação de filtros
  - [ ] Testar limpeza de filtros
  - [ ] Testar cache do React Query
  - [ ] Validar tipos TypeScript

---

## 📋 Fase 2: Otimização (Prioridade Média) 🟡

### Backend - Endpoint Dedicado e Performance

- [ ] **2.1. Criar DashboardPayrollsView**
  - [ ] Criar nova view em `protected_views.py`
  - [ ] Implementar paginação com `StandardResultsSetPagination`
  - [ ] Aplicar filtros do request
  - [ ] Implementar ordenação customizada
  - [ ] Adicionar rota em `urls.py`: `dashboard/payrolls/`

- [ ] **2.2. Adicionar Índices no Banco**
  - [ ] Criar migration para índice composto `[provider, status, reference_month]`
  - [ ] Criar índice para `created_at`
  - [ ] Executar migration
  - [ ] Validar performance com EXPLAIN

### Frontend - Tabela Paginada

- [ ] **2.3. Criar Componente PayrollsTable**
  - [ ] Implementar tabela com paginação
  - [ ] Conectar ao endpoint `/dashboard/payrolls/`
  - [ ] Adicionar suporte a ordenação
  - [ ] Implementar loading states

- [ ] **2.4. Otimizar Cache**
  - [ ] Configurar `cacheTime` apropriado
  - [ ] Implementar invalidação de cache
  - [ ] Adicionar prefetch para próxima página

### Testes e Validação

- [ ] **2.5. Testes de Performance**
  - [ ] Testar com 1000+ payrolls
  - [ ] Validar tempo de resposta < 500ms
  - [ ] Verificar uso de índices (EXPLAIN)
  - [ ] Testar paginação com diferentes page_size

---

## 📋 Fase 3: Analytics (Prioridade Baixa) 🟢

### Backend - Endpoint de Analytics

- [ ] **3.1. Criar DashboardAnalyticsView**
  - [ ] Implementar endpoint `/dashboard/analytics/`
  - [ ] Adicionar parâmetro `period` (3months, 6months, 12months)
  - [ ] Calcular timeline com dados mensais
  - [ ] Calcular métricas de crescimento
  - [ ] Criar projeções para próximo mês

### Frontend - Gráficos Avançados

- [ ] **3.2. Implementar Gráficos de Tendência**
  - [ ] Criar componente TrendChart
  - [ ] Integrar com endpoint de analytics
  - [ ] Adicionar seletor de período

- [ ] **3.3. Exportação de Relatórios**
  - [ ] Implementar export para Excel
  - [ ] Implementar export para PDF
  - [ ] Adicionar filtros na exportação

---

## 📊 Documentação

- [x] **Análise do Sistema**
  - [x] Identificar limitações atuais
  - [x] Propor 5 melhorias estruturadas
  - [x] Criar tabelas de priorização
  - [x] Definir roadmap em 3 fases

- [x] **Plano de Implementação**
  - [x] Código completo para cada fase
  - [x] Exemplos backend (Django)
  - [x] Exemplos frontend (React/TypeScript)
  - [x] Testes unitários e manuais

- [x] **Documentação da API**
  - [x] Documentar endpoint `/dashboard/`
  - [x] Documentar endpoint `/payrolls/`
  - [x] Documentar endpoint `/providers/`
  - [x] Criar estruturas TypeScript
  - [x] Adicionar exemplos práticos
  - [x] Documentar códigos de erro
  - [x] Criar guia de integração frontend

---

## 📁 Arquivos Relacionados

### Backend

- `protected_views.py` - Views do dashboard
- `urls.py` - Rotas da API
- `serializers.py` - Serializers
- `models.py` - Modelos de dados

### Frontend

- `src/types/index.ts` - Definições TypeScript
- `src/services/api.ts` - Chamadas à API
- `src/hooks/useDashboardData.ts` - Hook customizado
- `src/components/dashboard/DashboardFilters.tsx` - Componente de filtros
- `src/pages/Dashboard.tsx` - Página principal

### Documentação

- `analise_sistema_payroll.md` - Análise completa
- `implementation_plan.md` - Plano detalhado
- `dashboard_api_documentation.md` - Doc da API

---

## ✅ Critérios de Sucesso

### Fase 1

- [ ] Endpoint `/dashboard/` aceita e processa todos os filtros
- [ ] Frontend exibe componente de filtros funcional
- [ ] Dados são calculados no backend (não no frontend)
- [ ] Performance mantida < 1s com filtros

### Fase 2

- [ ] Endpoint `/dashboard/payrolls/` implementado
- [ ] Tabela paginada funcional
- [ ] Performance < 500ms com 1000+ registros
- [ ] Índices otimizados no banco

### Fase 3

- [ ] Analytics implementado
- [ ] Gráficos de tendência funcionais
- [ ] Exportação de relatórios disponível
