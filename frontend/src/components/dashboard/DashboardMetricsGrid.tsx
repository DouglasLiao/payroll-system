import { Grid } from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  Receipt as ReceiptIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { StatCard } from '../StatCard'
import { formatCurrency } from '../../utils/formatters'
import type {
  PayrollStats,
  PaginatedResponse,
  Payroll,
  Provider,
} from '../../types'

interface DashboardMetricsGridProps {
  payrollStats: PayrollStats
  providers: PaginatedResponse<Provider> | undefined
  payrolls: PaginatedResponse<Payroll> | undefined
  loading?: boolean
}

/**
 * Grid of metric cards for the dashboard
 * Displays key statistics about payrolls and payments
 */
export const DashboardMetricsGrid = ({
  payrollStats,
  providers,
  payrolls,
  loading = false,
}: DashboardMetricsGridProps) => {
  // Calculate pending payments (CLOSED status)
  const pendingPayments =
    payrolls?.results
      .filter((p: Payroll) => p.status === 'CLOSED')
      .reduce((sum: number, p: Payroll) => sum + parseFloat(p.net_value), 0) ||
    0

  // Calculate paid payments (PAID status)
  const paidPayments =
    payrolls?.results
      .filter((p: Payroll) => p.status === 'PAID')
      .reduce((sum: number, p: Payroll) => sum + parseFloat(p.net_value), 0) ||
    0

  return (
    <>
      {/* Payment Stats - Row 1 */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Pagamentos Pendentes"
          value={formatCurrency(pendingPayments)}
          icon={<MoneyIcon />}
          color="warning.main"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Pagamentos Realizados"
          value={formatCurrency(paidPayments)}
          icon={<TrendingUpIcon />}
          color="success.main"
          loading={loading}
        />
      </Grid>

      {/* Payroll Stats */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Total de Folhas"
          value={payrollStats.total}
          icon={<ReceiptIcon />}
          color="primary.main"
          subtitle={`${payrollStats.drafts} rascunhos, ${payrollStats.paid} pagas`}
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Total Prestadores"
          value={providers?.count || 0}
          icon={<PeopleIcon />}
          color="info.main"
          loading={loading}
        />
      </Grid>

      {/* Detailed Metrics - Row 2 */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Valor Total Folhas"
          value={formatCurrency(payrollStats.totalValue)}
          subtitle="Soma de todas as folhas"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Média por Folha"
          value={formatCurrency(payrollStats.avgValue)}
          subtitle="Valor médio calculado"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Folhas Fechadas"
          value={payrollStats.closed}
          color="info.main"
          subtitle="Aguardando pagamento"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Folhas Pagas"
          value={payrollStats.paid}
          color="success.main"
          subtitle="Finalizadas no mês"
          loading={loading}
        />
      </Grid>
    </>
  )
}
