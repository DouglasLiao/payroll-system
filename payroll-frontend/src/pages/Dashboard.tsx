import {
  Grid,
  Box,
  Typography,
  // ToggleButtonGroup,
  // ToggleButton,
} from '@mui/material'
import { useDashboardData } from '../hooks/useDashboardData'
import {
  DashboardMetricsGrid,
  FinancialChart,
  FinancialSummaryCard,
  CashFlowChart,
  RecentActivityCard,
  RecentPayrollsCard,
} from '../components/dashboard'

const Dashboard = () => {
  const { stats, monthlyData, trends, recentActivity, isLoading } =
    useDashboardData({ period: '1y' })

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
