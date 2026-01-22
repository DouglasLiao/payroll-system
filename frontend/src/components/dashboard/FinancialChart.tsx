import { useState, useMemo } from 'react'
import {
  Card,
  Typography,
  Box,
  ToggleButtonGroup,
  ToggleButton,
  useTheme,
} from '@mui/material'
import ReactApexChart from 'react-apexcharts'
import {
  getChartColors,
  getBaseChartOptions,
  formatCompactCurrency,
} from '../../utils/chartHelpers'
import { formatCurrency } from '../../utils/formatters'
import {
  sortMonthsChronologically,
  getLastNMonths,
} from '../../utils/dashboardCalculations'
import type { MonthlyData, ChartPeriod } from '../../types'

interface FinancialChartProps {
  monthlyData: MonthlyData
  loading?: boolean
}

const PERIODS: ChartPeriod[] = [
  { value: 3, label: '3 meses' },
  { value: 6, label: '6 meses' },
  { value: 12, label: '12 meses' },
]

/**
 * Enhanced financial chart with period selector and dual-axis visualization
 * Shows payroll status counts (bars) and total values (line)
 */
export const FinancialChart = ({
  monthlyData,
  loading = false,
}: FinancialChartProps) => {
  const theme = useTheme()
  const [period, setPeriod] = useState<3 | 6 | 12>(6)

  const colors = getChartColors(theme)

  // Get continuous list of months for the selected period
  const selectedMonths = useMemo(() => {
    return getLastNMonths(period)
  }, [period])

  // Memoize chart series based on selected months
  const chartSeries: ApexAxisChartSeries = useMemo(
    () =>
      selectedMonths.length > 0
        ? [
            {
              name: 'Rascunhos',
              type: 'column',
              data: selectedMonths.map((m) => monthlyData[m]?.draft || 0),
            },
            {
              name: 'Fechadas',
              type: 'column',
              data: selectedMonths.map((m) => monthlyData[m]?.closed || 0),
            },
            {
              name: 'Pagas',
              type: 'column',
              data: selectedMonths.map((m) => monthlyData[m]?.paid || 0),
            },
            {
              name: 'Valor Total',
              type: 'line',
              data: selectedMonths.map((m) => monthlyData[m]?.total || 0),
            },
          ]
        : [
            { name: 'Rascunhos', type: 'column', data: [0] },
            { name: 'Fechadas', type: 'column', data: [0] },
            { name: 'Pagas', type: 'column', data: [0] },
            { name: 'Valor Total', type: 'line', data: [0] },
          ],
    [selectedMonths, monthlyData]
  )

  // Memoize chart options
  const chartOptions: ApexCharts.ApexOptions = useMemo(
    () => ({
      ...getBaseChartOptions(theme),
      chart: {
        ...getBaseChartOptions(theme).chart,
        type: 'line',
        stacked: false,
      },
      colors: [colors.draft, colors.closed, colors.paid, colors.total],
      stroke: {
        width: [0, 0, 0, 3],
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
        type: 'category',
        categories: selectedMonths.length > 0 ? selectedMonths : ['N/A'],
        tickPlacement: 'on',
        labels: {
          ...getBaseChartOptions(theme).xaxis?.labels,
          style: {
            ...getBaseChartOptions(theme).xaxis?.labels?.style,
            fontSize: '11px',
          },
        },
      },
      yaxis: [
        {
          title: {
            text: 'Quantidade de Folhas',
            style: {
              color: theme.palette.text.secondary,
            },
          },
          labels: {
            formatter: (val) => Math.round(val).toString(),
            style: {
              colors: theme.palette.text.secondary,
            },
          },
        },
        {
          opposite: true,
          title: {
            text: 'Valor Total (R$)',
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
      ],
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
        y: [
          { formatter: (val) => `${val} folha(s)` },
          { formatter: (val) => `${val} folha(s)` },
          { formatter: (val) => `${val} folha(s)` },
          { formatter: (val) => formatCurrency(val) },
        ],
      },
    }),
    [theme, colors, selectedMonths]
  )

  return (
    <Card sx={{ p: 3 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Box>
          <Typography variant="h6">
            📊 Tendências de Folhas de Pagamento
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Evolução mensal das folhas por status e valor total
          </Typography>
        </Box>

        <ToggleButtonGroup
          value={period}
          exclusive
          onChange={(_, newPeriod) => {
            if (newPeriod !== null) setPeriod(newPeriod)
          }}
          size="small"
          aria-label="período do gráfico"
        >
          {PERIODS.map((p) => (
            <ToggleButton key={p.value} value={p.value} aria-label={p.label}>
              {p.label}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Box>

      {loading ? (
        <Box
          sx={{
            height: 350,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography color="text.secondary">Carregando dados...</Typography>
        </Box>
      ) : (
        <ReactApexChart
          key={`chart-${period}-${selectedMonths.length}`}
          options={chartOptions}
          series={chartSeries}
          type="line"
          height={350}
        />
      )}
    </Card>
  )
}
