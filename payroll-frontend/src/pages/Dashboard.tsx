import { useState } from 'react'
import {
  Grid,
  Box,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material'
import { useDashboardData } from '../hooks/useDashboardData'
import type { DashboardFilters } from '../services/api'
import {
  DashboardMetricsGrid,
  FinancialChart,
  FinancialSummaryCard,
  CashFlowChart,
  RecentActivityCard,
  RecentPayrollsCard,
} from '../components/dashboard'

const PERIOD_OPTIONS: Array<{
  value: DashboardFilters['period']
  label: string
}> = [
  { value: '7d', label: '7 dias' },
  { value: '30d', label: '30 dias' },
  { value: '90d', label: '90 dias' },
  { value: '1y', label: '1 ano' },
  { value: 'all', label: 'Tudo' },
]

const Dashboard = () => {
  const [period, setPeriod] = useState<DashboardFilters['period']>('30d')

  const { stats, monthlyData, trends, recentActivity, isLoading } =
    useDashboardData({ period })

  return (
    <Box sx={{ maxWidth: '100%', width: '100%', mt: 4 }}>
      {/* Header with Period Filter */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Typography variant="h4">Dashboard</Typography>

        <ToggleButtonGroup
          value={period}
          exclusive
          onChange={(_, newPeriod) => {
            if (newPeriod !== null) setPeriod(newPeriod)
          }}
          size="small"
          aria-label="período do dashboard"
        >
          {PERIOD_OPTIONS.map((option) => (
            <ToggleButton key={option.value} value={option.value as string}>
              {option.label}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Box>

      <Grid container spacing={3}>
        {/* Metrics Grid - 8 cards */}
        <DashboardMetricsGrid
          stats={stats}
          trends={trends}
          loading={isLoading}
        />

        {/* Financial Chart */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <FinancialChart monthlyData={monthlyData} loading={isLoading} />
        </Grid>

        {/* Financial Summary */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <FinancialSummaryCard
            stats={stats}
            trends={trends}
            loading={isLoading}
          />
        </Grid>

        {/* Cash Flow Analysis */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <CashFlowChart monthlyData={monthlyData} loading={isLoading} />
        </Grid>

        {/* Recent Activity */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <RecentActivityCard activities={recentActivity} loading={isLoading} />
        </Grid>

        {/* Recent Payrolls */}
        <Grid size={{ xs: 12 }}>
          <RecentPayrollsCard
            payrolls={recentActivity.slice(0, 5)}
            loading={isLoading}
          />
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
