import { Card, Typography, Box, useTheme, Alert } from '@mui/material'
import ReactApexChart from 'react-apexcharts'
import {
  getChartColors,
  getBaseChartOptions,
  formatCompactCurrency,
} from '../../utils/chartHelpers'
import { formatCurrency } from '../../utils/formatters'
import type { MonthlyData } from '../../types'

interface CashFlowChartProps {
  monthlyData: MonthlyData
  period?: 3 | 6 | 12
  loading?: boolean
}

/**
 * Cash flow chart showing income (paid) vs expenses (closed) over time
 */
export const CashFlowChart = ({
  monthlyData,
  period = 6,
  loading = false,
}: CashFlowChartProps) => {
  const theme = useTheme()
  const colors = getChartColors(theme)

  const sortedMonths = Object.keys(monthlyData).sort()
  const selectedMonths = sortedMonths.slice(-period)

  // Calculate income (paid payrolls) and expenses (closed payrolls)
  const incomeData = selectedMonths.map((m) => monthlyData[m]?.paidValue || 0)
  const expenseData = selectedMonths.map(
    (m) => monthlyData[m]?.closedValue || 0
  )

  // Calculate accumulated balance using reduce to avoid mutation
  const balanceData = selectedMonths.reduce<number[]>((acc, m) => {
    const income = monthlyData[m]?.paidValue || 0
    const expense = monthlyData[m]?.closedValue || 0
    const previousBalance = acc.length > 0 ? acc[acc.length - 1] : 0
    const newBalance = previousBalance + income - expense
    return [...acc, newBalance]
  }, [])

  // Check for negative months
  const hasNegativeMonths = balanceData.some((balance) => balance < 0)

  const chartSeries: ApexAxisChartSeries = [
    {
      name: 'Receitas (Pagas)',
      type: 'column',
      data: incomeData,
    },
    {
      name: 'Despesas (Fechadas)',
      type: 'column',
      data: expenseData,
    },
    {
      name: 'Saldo Acumulado',
      type: 'line',
      data: balanceData,
    },
  ]

  const chartOptions: ApexCharts.ApexOptions = {
    ...getBaseChartOptions(theme),
    chart: {
      ...getBaseChartOptions(theme).chart,
      type: 'line',
      stacked: false,
    },
    colors: [colors.income, colors.expense, colors.balance],
    stroke: {
      width: [0, 0, 3],
      curve: 'smooth',
    },
    plotOptions: {
      bar: {
        columnWidth: '50%',
      },
    },
    dataLabels: {
      enabled: false,
    },
    xaxis: {
      categories: selectedMonths.length > 0 ? selectedMonths : ['N/A'],
      labels: {
        ...getBaseChartOptions(theme).xaxis?.labels,
      },
    },
    yaxis: {
      title: {
        text: 'Valor (R$)',
        style: {
          color: theme.palette.text.secondary,
        },
      },
      labels: {
        formatter: (val) => formatCompactCurrency(val),
        style: {
          colors: theme.palette.text.secondary,
        },
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'center',
      labels: {
        colors: theme.palette.text.primary,
      },
    },
    tooltip: {
      shared: true,
      intersect: false,
      theme: theme.palette.mode,
      y: {
        formatter: (val) => formatCurrency(val),
      },
    },
  }

  // Calculate summary metrics
  const totalIncome = incomeData.reduce((sum, val) => sum + val, 0)
  const totalExpense = expenseData.reduce((sum, val) => sum + val, 0)
  const currentBalance = balanceData[balanceData.length - 1] || 0

  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        💸 Análise de Fluxo de Caixa
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Comparação entre receitas e despesas ao longo do tempo
      </Typography>

      {hasNegativeMonths && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Atenção: Detectado saldo negativo em alguns períodos
        </Alert>
      )}

      {loading ? (
        <Box
          sx={{
            height: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography color="text.secondary">Carregando dados...</Typography>
        </Box>
      ) : (
        <>
          <ReactApexChart
            options={chartOptions}
            series={chartSeries}
            type="line"
            height={300}
          />

          {/* Summary Metrics */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-around',
              mt: 3,
              pt: 2,
              borderTop: 1,
              borderColor: 'divider',
            }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                Total Receitas
              </Typography>
              <Typography variant="h6" color="success.main" fontWeight="600">
                {formatCurrency(totalIncome)}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                Total Despesas
              </Typography>
              <Typography variant="h6" color="error.main" fontWeight="600">
                {formatCurrency(totalExpense)}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                Saldo Atual
              </Typography>
              <Typography
                variant="h6"
                fontWeight="600"
                sx={{
                  color:
                    currentBalance >= 0
                      ? theme.palette.success.main
                      : theme.palette.error.main,
                }}
              >
                {formatCurrency(currentBalance)}
              </Typography>
            </Box>
          </Box>
        </>
      )}
    </Card>
  )
}
