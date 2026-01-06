import { Grid, Card, Typography, Box, Chip } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import ReactApexChart from 'react-apexcharts'
import { getDashboardStats } from '../services/api'

const Dashboard = () => {
  const { data, isLoading } = useQuery({ queryKey: ['dashboard'], queryFn: getDashboardStats })

  const chartOptions: ApexCharts.ApexOptions = {
    chart: { type: 'area', toolbar: { show: false } },
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth' },
    xaxis: { categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
    colors: ['#1890ff', '#52c41a'],
    fill: {
      type: 'gradient',
      gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.9, stops: [0, 90, 100] },
    },
  }

  const chartSeries = [
    { name: 'Paid', data: [3100, 4000, 2800, 5100, 4200, 10900] }, // Mock data for visual
    { name: 'Pending', data: [1100, 3200, 4500, 3200, 3400, 5200] },
  ]

  if (isLoading) return <Typography>Loading...</Typography>

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4 }}>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Total Pending
            </Typography>
            <Typography variant="h3">R$ {data?.stats.pending || 0}</Typography>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Total Paid
            </Typography>
            <Typography variant="h3" color="success.main">
              R$ {data?.stats.paid || 0}
            </Typography>
          </Card>
        </Grid>

        {/* Main Chart */}
        <Grid size={{ xs: 12, md: 8 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Payment Trends
            </Typography>
            <ReactApexChart options={chartOptions} series={chartSeries} type="area" height={350} />
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid size={{ xs: 12, md: 4 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Recent Activity
            </Typography>
            {data?.recent_activity.map((payment) => (
              <Box
                key={payment.id}
                sx={{
                  mb: 2,
                  pb: 2,
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant="subtitle1">{payment.provider_name}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {payment.reference}
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    R$ {payment.total_calculated}
                  </Typography>
                  <Chip
                    label={payment.status}
                    size="small"
                    color={payment.status === 'PAID' ? 'success' : 'default'}
                  />
                </Box>
              </Box>
            ))}
            {(!data?.recent_activity || data.recent_activity.length === 0) && (
              <Typography color="textSecondary">No recent payments.</Typography>
            )}
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
