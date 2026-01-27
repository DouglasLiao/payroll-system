# Plano de Implementação: Melhorias no Dashboard

## 📌 Objetivo

Melhorar o sistema de dashboard adicionando:

1. Filtros avançados no backend
2. Dados agregados mensais
3. Componente de filtros no frontend
4. Performance e escalabilidade

---

## Fase 1: Fundamentos (Prioridade Alta) 🔴

### Backend

#### 1.1. Expandir `ProtectedDashboardView`

**Arquivo:** `protected_views.py`

**Mudanças:**

1. Adicionar suporte a query parameters:
   - `start_date` (opcional)
   - `end_date` (opcional)
   - `provider_id` (opcional)
   - `status` (opcional)
   - `reference_month` (opcional)

2. Adicionar método auxiliar para filtrar payrolls:

```python
def get_filtered_payrolls(self, queryset, request):
    """Aplica filtros baseado nos query params"""
    # Filtro por período
    if start_date := request.query_params.get('start_date'):
        queryset = queryset.filter(created_at__gte=start_date)

    if end_date := request.query_params.get('end_date'):
        queryset = queryset.filter(created_at__lte=end_date)

    # Filtro por provider
    if provider_id := request.query_params.get('provider_id'):
        queryset = queryset.filter(provider_id=provider_id)

    # Filtro por status
    if status := request.query_params.get('status'):
        queryset = queryset.filter(status=status)

    # Filtro por mês de referência
    if reference_month := request.query_params.get('reference_month'):
        queryset = queryset.filter(reference_month=reference_month)

    return queryset
```

3. Adicionar agregação mensal:

```python
def get_monthly_data(self, payrolls):
    """Agrega dados por mês"""
    from collections import defaultdict

    monthly_data = defaultdict(lambda: {
        'total_payrolls': 0,
        'draft_count': 0,
        'closed_count': 0,
        'paid_count': 0,
        'total_value': Decimal('0.00'),
        'draft_value': Decimal('0.00'),
        'closed_value': Decimal('0.00'),
        'paid_value': Decimal('0.00'),
    })

    for payroll in payrolls:
        month = payroll.reference_month
        monthly_data[month]['total_payrolls'] += 1
        monthly_data[month]['total_value'] += payroll.net_value

        # Contar por status
        status_key = f"{payroll.status.lower()}_count"
        monthly_data[month][status_key] += 1

        # Somar valores por status
        value_key = f"{payroll.status.lower()}_value"
        monthly_data[month][value_key] += payroll.net_value

    return dict(monthly_data)
```

4. Adicionar top providers:

```python
def get_top_providers(self, payrolls, limit=5):
    """Retorna top N providers por valor total"""
    from django.db.models import Sum, Count, Avg

    top = (
        payrolls
        .values('provider__id', 'provider__name')
        .annotate(
            total_payrolls=Count('id'),
            total_value=Sum('net_value'),
            avg_value=Avg('net_value')
        )
        .order_by('-total_value')[:limit]
    )

    return [
        {
            'id': item['provider__id'],
            'name': item['provider__name'],
            'total_payrolls': item['total_payrolls'],
            'total_value': float(item['total_value']),
            'avg_value': float(item['avg_value']),
        }
        for item in top
    ]
```

5. Atualizar método `get()`:

```python
def get(self, request):
    user = request.user

    if user.role != "CUSTOMER_ADMIN":
        return Response(
            {"error": "Acesso negado. Apenas Customer Admin pode acessar o dashboard."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Base queryset
    company_payrolls = Payroll.objects.filter(provider__company=user.company)

    # Aplicar filtros
    filtered_payrolls = self.get_filtered_payrolls(company_payrolls, request)

    # Estatísticas básicas
    stats = {
        "total_providers": Provider.objects.filter(company=user.company).count(),
        "total_payrolls": filtered_payrolls.count(),
        "draft_payrolls": filtered_payrolls.filter(status="DRAFT").count(),
        "closed_payrolls": filtered_payrolls.filter(status="CLOSED").count(),
        "paid_payrolls": filtered_payrolls.filter(status="PAID").count(),

        # Valores totais
        "total_pending": filtered_payrolls.filter(status="CLOSED").aggregate(
            Sum("net_value")
        )["net_value__sum"] or 0,
        "total_paid": filtered_payrolls.filter(status="PAID").aggregate(
            Sum("net_value")
        )["net_value__sum"] or 0,

        # NOVO: Valores por status
        "draft_value": filtered_payrolls.filter(status="DRAFT").aggregate(
            Sum("net_value")
        )["net_value__sum"] or 0,
        "closed_value": filtered_payrolls.filter(status="CLOSED").aggregate(
            Sum("net_value")
        )["net_value__sum"] or 0,
        "paid_value": filtered_payrolls.filter(status="PAID").aggregate(
            Sum("net_value")
        )["net_value__sum"] or 0,

        # NOVO: Métricas financeiras
        "avg_payroll_value": filtered_payrolls.aggregate(
            Avg("net_value")
        )["net_value__avg"] or 0,
    }

    # NOVO: Dados mensais
    monthly_data = self.get_monthly_data(filtered_payrolls)

    # NOVO: Top providers
    top_providers = self.get_top_providers(filtered_payrolls)

    # Atividades recentes
    recent_payrolls = filtered_payrolls.order_by("-created_at")[:10]
    recent_activity = PayrollSerializer(recent_payrolls, many=True).data

    return Response({
        "stats": stats,
        "monthly_data": monthly_data,
        "top_providers": top_providers,
        "recent_activity": recent_activity,
        "filters_applied": {
            "start_date": request.query_params.get('start_date'),
            "end_date": request.query_params.get('end_date'),
            "provider_id": request.query_params.get('provider_id'),
            "status": request.query_params.get('status'),
            "reference_month": request.query_params.get('reference_month'),
        }
    })
```

---

### Frontend

#### 1.2. Atualizar Types

**Arquivo:** `src/types/index.ts`

```typescript
export interface DashboardFilters {
  startDate?: string;
  endDate?: string;
  providerId?: number;
  status?: PayrollStatus;
  referenceMonth?: string;
}

export interface DashboardStats {
  stats: {
    total_providers: number;
    total_payrolls: number;
    draft_payrolls: number;
    closed_payrolls: number;
    paid_payrolls: number;
    total_pending: number;
    total_paid: number;

    // NOVO
    draft_value: number;
    closed_value: number;
    paid_value: number;
    avg_payroll_value: number;
  };

  // NOVO
  monthly_data: {
    [month: string]: {
      total_payrolls: number;
      draft_count: number;
      closed_count: number;
      paid_count: number;
      total_value: number;
      draft_value: number;
      closed_value: number;
      paid_value: number;
    };
  };

  // NOVO
  top_providers: Array<{
    id: number;
    name: string;
    total_payrolls: number;
    total_value: number;
    avg_value: number;
  }>;

  recent_activity: Payroll[];

  // NOVO
  filters_applied: DashboardFilters;
}
```

#### 1.3. Atualizar API Service

**Arquivo:** `src/services/api.ts`

```typescript
export const getDashboardStats = async (filters?: DashboardFilters) => {
  const params = new URLSearchParams();

  if (filters?.startDate) params.append("start_date", filters.startDate);
  if (filters?.endDate) params.append("end_date", filters.endDate);
  if (filters?.providerId)
    params.append("provider_id", filters.providerId.toString());
  if (filters?.status) params.append("status", filters.status);
  if (filters?.referenceMonth)
    params.append("reference_month", filters.referenceMonth);

  const queryString = params.toString();
  const url = `/dashboard/${queryString ? `?${queryString}` : ""}`;

  const { data } = await api.get<DashboardStats>(url);
  return data;
};
```

#### 1.4. Refatorar Hook `useDashboardData`

**Arquivo:** `src/hooks/useDashboardData.ts`

```typescript
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { getDashboardStats, getProviders } from "../services/api";
import type {
  DashboardStats,
  DashboardFilters,
  PaginatedResponse,
  Provider,
} from "../types";

interface UseDashboardDataReturn {
  dashboardData: DashboardStats | undefined;
  providers: PaginatedResponse<Provider> | undefined;
  filters: DashboardFilters;
  setFilters: (filters: DashboardFilters) => void;
  isLoading: boolean;
  error: Error | null;
}

export const useDashboardData = (): UseDashboardDataReturn => {
  const [filters, setFilters] = useState<DashboardFilters>({});

  // Fetch dashboard stats with filters
  const {
    data: dashboardData,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useQuery({
    queryKey: ["dashboard", filters],
    queryFn: () => getDashboardStats(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });

  // Fetch providers for filter dropdown
  const {
    data: providers,
    isLoading: providersLoading,
    error: providersError,
  } = useQuery({
    queryKey: ["providers-filter"],
    queryFn: () => getProviders({ page_size: 1000 }),
    staleTime: 15 * 60 * 1000, // 15 minutes
  });

  const isLoading = dashboardLoading || providersLoading;
  const error = (dashboardError || providersError) as Error | null;

  return {
    dashboardData,
    providers,
    filters,
    setFilters,
    isLoading,
    error,
  };
};
```

#### 1.5. Criar Componente de Filtros

**Novo Arquivo:** `src/components/dashboard/DashboardFilters.tsx`

```typescript
import { useState } from 'react'
import {
  Card,
  Box,
  TextField,
  Select,
  MenuItem,
  Button,
  Autocomplete,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers'
import type { DashboardFilters, Provider, PayrollStatus } from '../../types'

interface DashboardFiltersProps {
  filters: DashboardFilters
  onFilterChange: (filters: DashboardFilters) => void
  providers: Provider[]
}

export const DashboardFilters = ({
  filters,
  onFilterChange,
  providers,
}: DashboardFiltersProps) => {
  const [localFilters, setLocalFilters] = useState<DashboardFilters>(filters)

  const handleApply = () => {
    onFilterChange(localFilters)
  }

  const handleClear = () => {
    setLocalFilters({})
    onFilterChange({})
  }

  return (
    <Card sx={{ p: 3, mb: 3 }}>
      <Grid container spacing={2}>
        {/* Date Range */}
        <Grid size={{ xs: 12, md: 3 }}>
          <DatePicker
            label="Data Inicial"
            value={localFilters.startDate || null}
            onChange={(date) =>
              setLocalFilters({ ...localFilters, startDate: date || undefined })
            }
            slotProps={{ textField: { fullWidth: true } }}
          />
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <DatePicker
            label="Data Final"
            value={localFilters.endDate || null}
            onChange={(date) =>
              setLocalFilters({ ...localFilters, endDate: date || undefined })
            }
            slotProps={{ textField: { fullWidth: true } }}
          />
        </Grid>

        {/* Provider */}
        <Grid size={{ xs: 12, md: 3 }}>
          <Autocomplete
            options={providers}
            getOptionLabel={(option) => option.name}
            value={
              providers.find((p) => p.id === localFilters.providerId) || null
            }
            onChange={(_, newValue) =>
              setLocalFilters({
                ...localFilters,
                providerId: newValue?.id,
              })
            }
            renderInput={(params) => (
              <TextField {...params} label="Prestador" fullWidth />
            )}
          />
        </Grid>

        {/* Status */}
        <Grid size={{ xs: 12, md: 3 }}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={localFilters.status || ''}
              onChange={(e) =>
                setLocalFilters({
                  ...localFilters,
                  status: e.target.value as PayrollStatus,
                })
              }
              label="Status"
            >
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="DRAFT">Rascunho</MenuItem>
              <MenuItem value="CLOSED">Fechada</MenuItem>
              <MenuItem value="PAID">Paga</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {/* Actions */}
        <Grid size={{ xs: 12 }}>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button variant="outlined" onClick={handleClear}>
              Limpar Filtros
            </Button>
            <Button variant="contained" onClick={handleApply}>
              Aplicar Filtros
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Card>
  )
}
```

#### 1.6. Atualizar Dashboard Page

**Arquivo:** `src/pages/Dashboard.tsx`

```typescript
import { Grid, Box, Typography, Skeleton, Card } from '@mui/material'
import { useDashboardData } from '../hooks/useDashboardData'
import {
  DashboardFilters,
  DashboardMetricsGrid,
  FinancialChart,
  // ... outros imports
} from '../components/dashboard'

const Dashboard = () => {
  const {
    dashboardData,
    providers,
    filters,
    setFilters,
    isLoading,
  } = useDashboardData()

  // ... loading state

  return (
    <Box sx={{ maxWidth: '100%', width: '100%', mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">Dashboard</Typography>
      </Box>

      {/* NOVO: Filtros */}
      <DashboardFilters
        filters={filters}
        onFilterChange={setFilters}
        providers={providers?.results || []}
      />

      <Grid container spacing={3}>
        {/* Usar dados do backend diretamente */}
        <DashboardMetricsGrid
          stats={dashboardData?.stats}
          monthlyData={dashboardData?.monthly_data}
          loading={isLoading}
        />

        {/* ... resto dos componentes */}
      </Grid>
    </Box>
  )
}
```

---

## Fase 2: Otimização (Prioridade Média) 🟡

### 2.1. Criar Endpoint de Payrolls Paginado

**Novo ViewSet:** `protected_views.py`

```python
class DashboardPayrollsView(APIView):
    """
    Endpoint dedicado para tabela de payrolls do dashboard
    com filtros e paginação.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .pagination import StandardResultsSetPagination

        user = request.user

        if user.role != "CUSTOMER_ADMIN":
            return Response(
                {"error": "Acesso negado."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Base queryset
        queryset = Payroll.objects.filter(
            provider__company=user.company
        ).select_related('provider')

        # Aplicar filtros
        queryset = self.get_filtered_payrolls(queryset, request)

        # Ordenação
        ordering = request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)

        # Paginação
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = PayrollSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
```

**Adicionar rota:** `urls.py`

```python
path("dashboard/payrolls/", DashboardPayrollsView.as_view(), name="dashboard_payrolls"),
```

### 2.2. Adicionar Índices no Banco

**Nova Migration:** `migrations/000X_add_dashboard_indexes.py`

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '000X_previous_migration'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(
                fields=['provider', 'status', 'reference_month'],
                name='payroll_dashboard_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='payroll',
            index=models.Index(
                fields=['created_at'],
                name='payroll_created_idx'
            ),
        ),
    ]
```

---

## Fase 3: Analytics (Prioridade Baixa) 🟢

### 3.1. Criar Endpoint de Analytics

**Arquivo:** `protected_views.py`

```python
class DashboardAnalyticsView(APIView):
    """
    Endpoint para dados analíticos e tendências.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ... implementação completa
        pass
```

---

## Verificação

### Testes Unitários

1. **Backend:**
   - Testar filtros do dashboard
   - Testar agregação mensal
   - Testar top providers
   - Testar paginação

2. **Frontend:**
   - Testar hook `useDashboardData` com filtros
   - Testar componente `DashboardFilters`
   - Testar cache e invalidação

### Testes Manuais

1. Aplicar filtros e verificar resultados
2. Testar performance com 1000+ folhas
3. Validar dados agregados mensais
4. Verificar responsividade dos filtros
