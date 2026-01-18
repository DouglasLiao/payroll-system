import { Grid, Box, Typography, Skeleton, Card } from '@mui/material'
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
  const {
    payrollStats,
    monthlyData,
    financialMetrics,
    payrolls,
    providers,
    dashboardData,
    isLoading,
  } = useDashboardData()

  if (isLoading) {
    return (
      <Box>
        <Typography variant="h4" sx={{ mb: 4 }}>
          Dashboard
        </Typography>
        <Grid container spacing={3}>
          {[...Array(8)].map((_, i) => (
            <Grid key={i} size={{ xs: 12, sm: 6, md: 3 }}>
              <Card sx={{ p: 3 }}>
                <Skeleton variant="text" width={100} />
                <Skeleton
                  variant="rectangular"
                  height={40}
                  width={150}
                  sx={{ mt: 2 }}
                />
              </Card>
            </Grid>
          ))}
          <Grid size={{ xs: 12 }}>
            <Card sx={{ p: 3 }}>
              <Skeleton variant="text" width={150} sx={{ mb: 2 }} />
              <Skeleton variant="rectangular" height={350} />
            </Card>
          </Grid>
        </Grid>
      </Box>
    )
  }

  return (
    <Box sx={{ maxWidth: '100%', width: '100%', mt: 4 }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
        }}
      >
        <Typography variant="h4">Dashboard</Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Metrics Grid - 8 cards */}
        <DashboardMetricsGrid
          payrollStats={payrollStats}
          providers={providers}
          payrolls={payrolls}
          loading={isLoading}
        />

        {/* Financial Chart */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <FinancialChart monthlyData={monthlyData} loading={isLoading} />
        </Grid>

        {/* Financial Summary */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <FinancialSummaryCard
            payrollStats={payrollStats}
            financialMetrics={financialMetrics}
            loading={isLoading}
          />
        </Grid>

        {/* Cash Flow Analysis */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <CashFlowChart monthlyData={monthlyData} loading={isLoading} />
        </Grid>

        {/* Recent Activity */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <RecentActivityCard
            activities={dashboardData?.recent_activity || []}
            loading={isLoading}
          />
        </Grid>

        {/* Recent Payrolls */}
        <Grid size={{ xs: 12 }}>
          <RecentPayrollsCard
            payrolls={payrolls?.results || []}
            loading={isLoading}
          />
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
