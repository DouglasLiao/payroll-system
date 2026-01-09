import { Grid, Card, Typography, Box, Skeleton } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import ReactApexChart from 'react-apexcharts'
import {
  TrendingUp as TrendingUpIcon,
  Receipt as ReceiptIcon,
  AttachMoney as MoneyIcon,
  People as PeopleIcon,
} from '@mui/icons-material'
import { getDashboardStats, getPayrolls, getProviders } from '../services/api'
import { formatCurrency } from '../utils/formatters'
import { StatusChip } from '../components/StatusChip'
import { StatCard } from '../components/StatCard'
import type { Payroll } from '../types'

const Dashboard = () => {
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardStats
  })

  const { data: payrolls, isLoading: payrollsLoading } = useQuery({
    queryKey: ['payrolls-dashboard'],
    queryFn: () => getPayrolls({}),
  })

  const { data: providers, isLoading: providersLoading } = useQuery({
    queryKey: ['providers-dashboard'],
    queryFn: getProviders,
  })

  const isLoading = dashboardLoading || payrollsLoading || providersLoading

  // Calculate payroll metrics
  const payrollStats = payrolls ? {
    total: payrolls.length,
    drafts: payrolls.filter((p: Payroll) => p.status === 'DRAFT').length,
    closed: payrolls.filter((p: Payroll) => p.status === 'CLOSED').length,
    paid: payrolls.filter((p: Payroll) => p.status === 'PAID').length,
    totalValue: payrolls.reduce((sum: number, p: Payroll) => sum + parseFloat(p.net_value), 0),
    avgValue: payrolls.length > 0
      ? payrolls.reduce((sum: number, p: Payroll) => sum + parseFloat(p.net_value), 0) / payrolls.length
      : 0,
  } : { total: 0, drafts: 0, closed: 0, paid: 0, totalValue: 0, avgValue: 0 }

  // Group payrolls by month for chart
  const monthlyData = payrolls ? payrolls.reduce((acc: any, p: Payroll) => {
    const month = p.reference_month
    if (!acc[month]) {
      acc[month] = { draft: 0, closed: 0, paid: 0, total: 0 }
    }
    acc[month][p.status.toLowerCase() as 'draft' | 'closed' | 'paid']++
    acc[month].total += parseFloat(p.net_value)
    return acc
  }, {}) : {}

  const sortedMonths = Object.keys(monthlyData).sort()
  const last6Months = sortedMonths.slice(-6)

  const chartOptions: ApexCharts.ApexOptions = {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      stacked: false,
    },
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 2 },
    xaxis: {
      categories: last6Months.length > 0 ? last6Months : ['N/A'],
      labels: { style: { fontSize: '12px' } }
    },
    yaxis: [
      {
        title: { text: 'Quantidade' },
        labels: { formatter: (val) => Math.round(val).toString() }
      },
      {
        opposite: true,
        title: { text: 'Valor (R$)' },
        labels: {
          formatter: (val) => `R$ ${(val / 1000).toFixed(1)}k`
        }
      }
    ],
    colors: ['#FFA726', '#42A5F5', '#66BB6A', '#AB47BC'],
    legend: {
      position: 'top',
      horizontalAlign: 'center',
    },
    tooltip: {
      shared: true,
      intersect: false,
      y: [
        { formatter: (val) => `${val} folha(s)` },
        { formatter: (val) => `${val} folha(s)` },
        { formatter: (val) => `${val} folha(s)` },
        { formatter: (val) => formatCurrency(val) },
      ]
    }
  }

  const chartSeries = last6Months.length > 0 ? [
    {
      name: 'Rascunhos',
      type: 'column',
      data: last6Months.map(m => monthlyData[m]?.draft || 0)
    },
    {
      name: 'Fechadas',
      type: 'column',
      data: last6Months.map(m => monthlyData[m]?.closed || 0)
    },
    {
      name: 'Pagas',
      type: 'column',
      data: last6Months.map(m => monthlyData[m]?.paid || 0)
    },
    {
      name: 'Valor Total',
      type: 'line',
      data: last6Months.map(m => monthlyData[m]?.total || 0)
    },
  ] : [
    { name: 'Rascunhos', type: 'column', data: [0] },
    { name: 'Fechadas', type: 'column', data: [0] },
    { name: 'Pagas', type: 'column', data: [0] },
    { name: 'Valor Total', type: 'line', data: [0] },
  ]

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
                <Skeleton variant="rectangular" height={40} width={150} sx={{ mt: 2 }} />
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">
          Visão geral do sistema
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Payments Stats Legacy */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Pagamentos Pendentes"
            value={formatCurrency(dashboardData?.stats.pending || 0)}
            icon={<MoneyIcon />}
            color="warning.main"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Pagamentos Realizados"
            value={formatCurrency(dashboardData?.stats.paid || 0)}
            icon={<TrendingUpIcon />}
            color="success.main"
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
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Total Prestadores"
            value={providers?.length || 0}
            icon={<PeopleIcon />}
            color="info.main"
          />
        </Grid>

        {/* Second row - Payroll detailed metrics */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Valor Total Folhas"
            value={formatCurrency(payrollStats.totalValue)}
            subtitle="Soma de todas as folhas"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Média por Folha"
            value={formatCurrency(payrollStats.avgValue)}
            subtitle="Valor médio calculado"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Folhas Fechadas"
            value={payrollStats.closed}
            color="info.main"
            subtitle="Aguardando pagamento"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Folhas Pagas"
            value={payrollStats.paid}
            color="success.main"
            subtitle="Finalizadas no mês"
          />
        </Grid>

        {/* Payroll Trends Chart */}
        <Grid size={{ xs: 12, lg: 8 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              📊 Tendências de Folhas de Pagamento
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Evolução mensal das folhas por status e valor total
            </Typography>
            <ReactApexChart
              options={chartOptions}
              series={chartSeries}
              type="line"
              height={350}
            />
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid size={{ xs: 12, lg: 4 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              🕐 Atividade Recente
            </Typography>
            {dashboardData?.recent_activity.map((payment) => (
              <Box
                key={payment.id}
                sx={{
                  mb: 2,
                  pb: 2,
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                  display: 'flex',
                  justifyContent: 'space-between',
                }}
              >
                <Box>
                  <Typography variant="subtitle2">{payment.provider_name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {payment.reference}
                  </Typography>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {formatCurrency(payment.total_calculated)}
                  </Typography>
                  <StatusChip status={payment.status} />
                </Box>
              </Box>
            ))}
            {(!dashboardData?.recent_activity || dashboardData.recent_activity.length === 0) && (
              <Typography color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                Nenhuma atividade recente
              </Typography>
            )}
          </Card>
        </Grid>

        {/* Recent Payrolls */}
        <Grid size={{ xs: 12 }}>
          <Card sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              🧾 Últimas Folhas de Pagamento
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {payrolls?.slice(0, 5).map((payroll: Payroll) => (
                <Card
                  key={payroll.id}
                  variant="outlined"
                  sx={{
                    p: 2,
                    minWidth: 200,
                    flex: '1 1 calc(20% - 16px)',
                    '&:hover': { boxShadow: 2, borderColor: 'primary.main' }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {payroll.reference_month}
                    </Typography>
                    <StatusChip status={payroll.status as any} />
                  </Box>
                  <Typography variant="subtitle2" noWrap>
                    {payroll.provider_name}
                  </Typography>
                  <Typography variant="h6" color="primary.main" sx={{ mt: 1 }}>
                    {formatCurrency(payroll.net_value)}
                  </Typography>
                </Card>
              ))}
              {(!payrolls || payrolls.length === 0) && (
                <Typography color="text.secondary" sx={{ textAlign: 'center', width: '100%', py: 3 }}>
                  Nenhuma folha cadastrada ainda
                </Typography>
              )}
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
