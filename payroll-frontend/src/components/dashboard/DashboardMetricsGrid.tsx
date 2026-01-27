import { Grid } from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Receipt as ReceiptIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { StatCard } from '../StatCard'
import { formatCurrency } from '../../utils/formatters'
import type { EnhancedDashboardStats } from '../../types'

interface DashboardMetricsGridProps {
  stats?: EnhancedDashboardStats['stats']
  trends?: EnhancedDashboardStats['trends']
  loading?: boolean
}

/**
 * Grid of metric cards for the dashboard
 * Displays key statistics about payrolls and payments from backend
 */
export const DashboardMetricsGrid = ({
  stats,
  trends,
  loading = false,
}: DashboardMetricsGridProps) => {
  if (!stats) {
    return null
  }

  // Calculate trend indicator for value change
  const valueChange = trends?.period_vs_previous.value_change || 0
  const TrendIcon = valueChange >= 0 ? TrendingUpIcon : TrendingDownIcon
  const trendColor = valueChange >= 0 ? 'success.main' : 'error.main'

  return (
    <>
      {/* Payment Stats - Row 1 */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Pagamentos Pendentes"
          value={formatCurrency(stats.financial.pending_value)}
          icon={<MoneyIcon />}
          color="warning.main"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Pagamentos Realizados"
          value={formatCurrency(stats.financial.paid_value)}
          icon={<TrendingUpIcon />}
          color="success.main"
          loading={loading}
        />
      </Grid>

      {/* Payroll Stats */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Total de Folhas"
          value={stats.payrolls.total}
          icon={<ReceiptIcon />}
          color="primary.main"
          subtitle={`${stats.payrolls.draft} rascunhos, ${stats.payrolls.paid} pagas`}
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Total Prestadores"
          value={stats.total_providers}
          icon={<PeopleIcon />}
          color="info.main"
          loading={loading}
        />
      </Grid>

      {/* Detailed Metrics - Row 2 */}
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Valor Total Folhas"
          value={formatCurrency(stats.financial.total_value)}
          subtitle={
            valueChange !== 0
              ? `${valueChange >= 0 ? '+' : ''}${valueChange.toFixed(1)}% vs período anterior`
              : 'Soma de todas as folhas'
          }
          icon={valueChange !== 0 ? <TrendIcon /> : undefined}
          color={valueChange !== 0 ? trendColor : undefined}
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Média por Folha"
          value={formatCurrency(stats.financial.average_payroll)}
          subtitle="Valor médio calculado"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Folhas Fechadas"
          value={stats.payrolls.closed}
          color="info.main"
          subtitle="Aguardando pagamento"
          loading={loading}
        />
      </Grid>
      <Grid size={{ xs: 12, sm: 6, md: 3 }}>
        <StatCard
          title="Folhas Pagas"
          value={stats.payrolls.paid}
          color="success.main"
          subtitle={
            trends && trends.monthly_growth_percentage !== 0
              ? `${trends.monthly_growth_percentage >= 0 ? '+' : ''}${trends.monthly_growth_percentage.toFixed(1)}% crescimento mensal`
              : 'Finalizadas no período'
          }
          loading={loading}
        />
      </Grid>
    </>
  )
}
