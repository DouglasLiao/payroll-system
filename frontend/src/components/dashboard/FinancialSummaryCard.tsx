import { Card, Typography, Box, Divider, useTheme } from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  AccountBalance,
} from '@mui/icons-material'
import { formatCurrency } from '../../utils/formatters'
import { getTrendColor, getTrendIndicator } from '../../utils/chartHelpers'
import type { PayrollStats, FinancialMetrics } from '../../types'

interface FinancialSummaryCardProps {
  payrollStats: PayrollStats
  financialMetrics: FinancialMetrics
  loading?: boolean
}

/**
 * Card displaying financial summary and key indicators
 */
export const FinancialSummaryCard = ({
  payrollStats,
  financialMetrics,
  loading = false,
}: FinancialSummaryCardProps) => {
  const theme = useTheme()
  const growthRate = financialMetrics.monthlyGrowth
  const trendColor = getTrendColor(growthRate, theme)

  const getTrendIcon = () => {
    if (growthRate > 0) return <TrendingUp sx={{ color: trendColor }} />
    if (growthRate < 0) return <TrendingDown sx={{ color: trendColor }} />
    return <TrendingFlat sx={{ color: trendColor }} />
  }

  if (loading) {
    return (
      <Card sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>
          💰 Resumo Financeiro
        </Typography>
        <Typography color="text.secondary">Carregando...</Typography>
      </Card>
    )
  }

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
          {formatCurrency(payrollStats.totalValue)}
        </Typography>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Monthly Average */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Média Mensal
        </Typography>
        <Typography variant="h6" fontWeight="600">
          {formatCurrency(financialMetrics.avgMonthlyValue)}
        </Typography>
      </Box>

      {/* Growth Rate */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Taxa de Crescimento
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
              financialMetrics.cashFlow >= 0
                ? theme.palette.success.main
                : theme.palette.error.main,
          }}
        >
          {formatCurrency(financialMetrics.cashFlow)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {financialMetrics.cashFlow >= 0 ? 'Positivo' : 'Negativo'}
        </Typography>
      </Box>

      {/* Projection */}
      <Box>
        <Typography variant="caption" color="text.secondary">
          Projeção Próximo Mês
        </Typography>
        <Typography variant="h6" fontWeight="600" color="info.main">
          {formatCurrency(financialMetrics.projectedNextMonth)}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Baseado em média móvel
        </Typography>
      </Box>
    </Card>
  )
}
