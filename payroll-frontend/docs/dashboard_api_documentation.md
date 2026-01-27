# 📚 Documentação da API - Dashboard Payroll

> **Versão:** 1.0.0  
> **Data:** 26/01/2026  
> **Base URL:** `http://localhost:8000/`

---

## 📖 Índice

1. [Visão Geral](#visão-geral)
2. [Autenticação](#autenticação)
3. [Endpoints](#endpoints)
   - [Dashboard Stats](#get-apidashboard)
   - [Payrolls List](#get-apipayrolls)
   - [Providers List](#get-apiproviders)
4. [Estruturas de Dados](#estruturas-de-dados)
5. [Códigos de Erro](#códigos-de-erro)
6. [Guia de Integração Frontend](#guia-de-integração-frontend)
7. [Roadmap - Novos Endpoints](#roadmap---novos-endpoints)

---

## Visão Geral

A API do Dashboard fornece dados estatísticos e operacionais para o sistema de folha de pagamento. Todos os endpoints requerem autenticação via JWT e aplicam filtros de multi-tenancy automaticamente baseado na empresa do usuário logado.

### Requisitos

- **Autenticação:** Bearer Token (JWT)
- **Permissões:** Customer Admin (para dashboard)
- **Rate Limit:** Não implementado
- **CORS:** Habilitado para desenvolvimento local

---

## Autenticação

Todos os endpoints requerem um token JWT válido no header:

```http
Authorization: Bearer <access_token>
```

### Obter Token

```http
POST /auth/login/
Content-Type: application/json

{
  "username": "admin@empresa.com",
  "password": "senha123"
}
```

**Response 200:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "CUSTOMER_ADMIN",
    "company_name": "Empresa XYZ"
  }
}
```

---

## Endpoints

### `GET /dashboard/`

Retorna estatísticas agregadas do dashboard para a empresa do usuário logado.

#### Permissões

- ✅ **Customer Admin** - Acesso total aos dados da sua empresa
- ❌ **Provider** - Acesso negado
- ✅ **Super Admin** - Acesso total (todas as empresas)

#### Query Parameters

| Parâmetro | Tipo | Obrigatório | Descrição                         | Exemplo |
| --------- | ---- | ----------- | --------------------------------- | ------- |
| (nenhum)  | -    | -           | Endpoint atual não aceita filtros | -       |

> ⚠️ **Limitação Atual:** Este endpoint não possui suporte a filtros. Veja [Roadmap](#roadmap---novos-endpoints) para melhorias futuras.

#### Response 200 - Success

```json
{
  "stats": {
    "total_providers": 10,
    "total_payrolls": 50,
    "draft_payrolls": 15,
    "closed_payrolls": 20,
    "paid_payrolls": 15,
    "total_pending": 45000.0,
    "total_paid": 67500.0
  },
  "recent_activity": [
    {
      "id": 1,
      "provider": 5,
      "provider_name": "João Silva",
      "reference_month": "01/2026",
      "status": "PAID",
      "status_display": "Paga",
      "base_value": "2200.00",
      "net_value": "2150.00",
      "created_at": "2026-01-15T10:30:00Z",
      "paid_at": "2026-01-20T14:00:00Z"
    }
  ]
}
```

#### Response 403 - Forbidden

```json
{
  "error": "Acesso negado. Apenas Customer Admin pode acessar o dashboard."
}
```

#### Exemplo de Uso (TypeScript)

```typescript
// Service
export const getDashboardStats = async () => {
  const { data } = await api.get<DashboardStats>('/dashboard/')
  return data
}

// Hook
const { data, isLoading, error } = useQuery({
  queryKey: ['dashboard'],
  queryFn: getDashboardStats,
})
```

---

### `GET /payrolls/`

Retorna lista paginada de folhas de pagamento da empresa.

#### Permissões

- ✅ **Customer Admin** - Ver todas as folhas da empresa
- ✅ **Provider** - Ver apenas suas próprias folhas
- ✅ **Super Admin** - Ver todas as folhas

#### Query Parameters

| Parâmetro         | Tipo   | Obrigatório | Descrição                     | Exemplo                   |
| ----------------- | ------ | ----------- | ----------------------------- | ------------------------- |
| `page`            | number | Não         | Número da página (padrão: 1)  | `page=2`                  |
| `page_size`       | number | Não         | Itens por página (padrão: 10) | `page_size=50`            |
| `status`          | string | Não         | Filtrar por status            | `status=PAID`             |
| `reference_month` | string | Não         | Mês de referência MM/YYYY     | `reference_month=01/2026` |
| `provider`        | number | Não         | ID do provider                | `provider=5`              |
| `ordering`        | string | Não         | Campo de ordenação            | `ordering=-created_at`    |

#### Valores Válidos

**Status:**

- `DRAFT` - Rascunho
- `CLOSED` - Fechada
- `PAID` - Paga

**Ordering:**

- `reference_month` - Por mês de referência
- `-reference_month` - Por mês (decrescente)
- `created_at` - Por data de criação
- `-created_at` - Por data de criação (decrescente)
- `net_value` - Por valor líquido
- `-net_value` - Por valor líquido (decrescente)

#### Response 200 - Success

```json
{
  "count": 150,
  "next": "http://localhost:8000/payrolls/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "provider": 5,
      "provider_name": "João Silva",
      "reference_month": "01/2026",
      "status": "PAID",
      "status_display": "Paga",

      "base_value": "2200.00",
      "hourly_rate": "10.00",
      "advance_value": "880.00",
      "remaining_value": "1320.00",

      "overtime_hours_50": "10.00",
      "holiday_hours": "8.00",
      "night_hours": "20.00",
      "late_minutes": 30,
      "absence_hours": "0.00",

      "overtime_amount": "150.00",
      "holiday_amount": "160.00",
      "dsr_amount": "25.00",
      "night_shift_amount": "40.00",
      "total_earnings": "2575.00",

      "late_discount": "5.00",
      "absence_discount": "0.00",
      "vt_discount": "220.00",
      "manual_discounts": "0.00",
      "total_discounts": "225.00",

      "gross_value": "2575.00",
      "net_value": "2350.00",

      "notes": "Folha de janeiro",
      "closed_at": "2026-01-20T10:00:00Z",
      "paid_at": "2026-01-20T14:00:00Z",
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-01-20T14:00:00Z"
    }
  ]
}
```

#### Exemplo de Uso (TypeScript)

```typescript
interface PayrollFilters {
  page?: number
  page_size?: number
  status?: PayrollStatus
  reference_month?: string
  provider?: number
  ordering?: string
}

export const getPayrolls = async (filters: PayrollFilters = {}) => {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) {
      params.append(key, String(value))
    }
  })

  const { data } = await api.get<PaginatedResponse<Payroll>>(
    `/payrolls/?${params.toString()}`
  )
  return data
}
```

---

### `GET /providers/`

Retorna lista paginada de prestadores da empresa.

#### Query Parameters

| Parâmetro        | Tipo   | Obrigatório | Descrição           | Exemplo              |
| ---------------- | ------ | ----------- | ------------------- | -------------------- |
| `page`           | number | Não         | Número da página    | `page=1`             |
| `page_size`      | number | Não         | Itens por página    | `page_size=100`      |
| `role`           | string | Não         | Filtrar por função  | `role=Desenvolvedor` |
| `payment_method` | string | Não         | Método de pagamento | `payment_method=PIX` |
| `ordering`       | string | Não         | Ordenação           | `ordering=name`      |

#### Response 200 - Success

```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "João Silva",
      "role": "Desenvolvedor Full Stack",
      "monthly_value": "2200.00",
      "monthly_hours": 220,
      "advance_enabled": true,
      "advance_percentage": "40.00",
      "vt_value": "220.00",
      "payment_method": "PIX",
      "pix_key": "joao@email.com",
      "email": "joao@email.com",
      "company": 1,
      "created_at": "2025-12-01T00:00:00Z"
    }
  ]
}
```

---

## Estruturas de Dados

### DashboardStats

```typescript
interface DashboardStats {
  stats: {
    total_providers: number
    total_payrolls: number
    draft_payrolls: number
    closed_payrolls: number
    paid_payrolls: number
    total_pending: number
    total_paid: number
  }
  recent_activity: Payroll[]
}
```

### Payroll

```typescript
interface Payroll {
  id: number
  provider: number
  provider_name: string
  reference_month: string
  status: PayrollStatus
  status_display: string

  base_value: string
  hourly_rate: string
  advance_value: string
  remaining_value: string

  overtime_hours_50: string
  holiday_hours: string
  night_hours: string
  late_minutes: number
  absence_hours: string

  overtime_amount: string
  holiday_amount: string
  dsr_amount: string
  night_shift_amount: string
  total_earnings: string

  late_discount: string
  absence_discount: string
  vt_discount: string
  manual_discounts: string
  total_discounts: string

  gross_value: string
  net_value: string

  notes?: string
  closed_at?: string
  paid_at?: string
  created_at: string
  updated_at: string
}

type PayrollStatus = 'DRAFT' | 'CLOSED' | 'PAID'
```

### Provider

```typescript
interface Provider {
  id: number
  name: string
  role: string
  monthly_value: string
  monthly_hours: number
  advance_enabled: boolean
  advance_percentage: string
  vt_value: string
  payment_method: PaymentMethod
  pix_key?: string
  bank_name?: string
  bank_agency?: string
  bank_account?: string
  email?: string
  company: number
  created_at: string
}

type PaymentMethod = 'PIX' | 'TED' | 'TRANSFER'
```

---

## Códigos de Erro

| Código | Significado    | Quando Ocorre           |
| ------ | -------------- | ----------------------- |
| `200`  | OK             | Requisição bem-sucedida |
| `400`  | Bad Request    | Parâmetros inválidos    |
| `401`  | Unauthorized   | Token inválido/ausente  |
| `403`  | Forbidden      | Sem permissão           |
| `404`  | Not Found      | Recurso não encontrado  |
| `500`  | Internal Error | Erro no servidor        |

---

## Guia de Integração Frontend

### Setup Básico

```typescript
// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

### Usando React Query

```typescript
import { useQuery } from '@tanstack/react-query'
import { getDashboardStats } from '../services/api'

export const useDashboard = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardStats,
    staleTime: 5 * 60 * 1000,
  })

  return { dashboardData: data, isLoading }
}
```

---

## Roadmap - Novos Endpoints

### Fase 1: Filtros no Dashboard

**Novos parâmetros para `/dashboard/`:**

- `start_date`, `end_date`, `provider_id`, `status`, `reference_month`

**Novos campos no response:**

- `monthly_data` - Dados agregados por mês
- `top_providers` - Top 5 prestadores
- `filters_applied` - Filtros aplicados

### Fase 2: Endpoint Dedicado

**Novo:** `GET /dashboard/payrolls/`  
Endpoint otimizado para tabelas com paginação

### Fase 3: Analytics

**Novo:** `GET /dashboard/analytics/`  
Análise temporal e tendências
