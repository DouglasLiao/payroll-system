import { Card, Typography, Box, Divider, useTheme } from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  AccountBalance,
} from '@mui/icons-material'
import { formatCurrency } from '../../utils/formatters'
import { getTrendColor, getTrendIndicator } from '../../utils/chartHelpers'
import type { EnhancedDashboardStats } from '../../types'

interface FinancialSummaryCardProps {
  stats?: EnhancedDashboardStats['stats']
  trends?: EnhancedDashboardStats['trends']
  loading?: boolean
}

/**
 * Card displaying financial summary and key indicators from backend
 */
export const FinancialSummaryCard = ({
  stats,
  trends,
  loading = false,
}: FinancialSummaryCardProps) => {
  const theme = useTheme()

  if (loading || !stats || !trends) {
    return (
      <Card sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>
          💰 Resumo Financeiro
        </Typography>
        <Typography color="text.secondary">Carregando...</Typography>
      </Card>
    )
  }

  const growthRate = trends.monthly_growth_percentage
  const trendColor = getTrendColor(growthRate, theme)

  const getTrendIcon = () => {
    if (growthRate > 0) return <TrendingUp sx={{ color: trendColor }} />
    if (growthRate < 0) return <TrendingDown sx={{ color: trendColor }} />
    return <TrendingFlat sx={{ color: trendColor }} />
  }

  // Calculate cash flow from stats
  const cashFlow = stats.financial.paid_value - stats.financial.pending_value

  return (
    <Card sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <AccountBalance sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">Resumo Financeiro</Typography>
      </Box>

      {/* Total Value */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="caption" color="text.secondary">
          Valor Total de Folhas
        </Typography>
        <Typography variant="h4" fontWeight="bold" color="primary.main">
          {formatCurrency(stats.financial.total_value)}
        </Typography>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Average Payroll */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Média por Folha
        </Typography>
        <Typography variant="h6" fontWeight="600">
          {formatCurrency(stats.financial.average_payroll)}
        </Typography>
      </Box>

      {/* Growth Rate */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Crescimento Mensal
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getTrendIcon()}
          <Typography variant="h6" fontWeight="600" sx={{ color: trendColor }}>
            {getTrendIndicator(growthRate)} {Math.abs(growthRate).toFixed(1)}%
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          vs. mês anterior
        </Typography>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Cash Flow */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Fluxo de Caixa
        </Typography>
        <Typography
          variant="h6"
          fontWeight="600"
          sx={{
            color:
              cashFlow >= 0
                ? theme.palette.success.main
                : theme.palette.error.main,
          }}
        >
          {formatCurrency(cashFlow)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Pago - Pendente
        </Typography>
      </Box>

      {/* Period Comparison */}
      <Box>
        <Typography variant="caption" color="text.secondary">
          Variação vs Período Anterior
        </Typography>
        <Typography
          variant="h6"
          fontWeight="600"
          color={
            trends.period_vs_previous.value_change >= 0
              ? 'success.main'
              : 'error.main'
          }
        >
          {trends.period_vs_previous.value_change >= 0 ? '+' : ''}
          {trends.period_vs_previous.value_change.toFixed(1)}%
        </Typography>
        <Typography variant="caption" color="text.secondary">
          em valor total
        </Typography>
      </Box>
    </Card>
  )
}
