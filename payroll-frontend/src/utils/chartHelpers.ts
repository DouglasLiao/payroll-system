import type { Theme } from '@mui/material'
import { formatCurrency } from 'src/utils/formatters'

/**
 * Get chart colors optimized for both light and dark modes
 */
export const getChartColors = (theme: Theme) => {
  const isDark = theme.palette.mode === 'dark'

  return {
    draft: isDark ? '#FFA726' : '#FF9800', // Orange
    closed: isDark ? '#42A5F5' : '#2196F3', // Blue
    paid: isDark ? '#66BB6A' : '#4CAF50', // Green
    total: isDark ? '#AB47BC' : '#9C27B0', // Purple
    income: isDark ? '#26C6DA' : '#00BCD4', // Cyan
    expense: isDark ? '#EF5350' : '#F44336', // Red
    balance: isDark ? '#9CCC65' : '#8BC34A', // Light Green
    projection: isDark ? '#78909C' : '#607D8B', // Blue Grey
  }
}

/**
 * Format chart values based on type
 */
export const formatChartValue = (
  value: number,
  type: 'currency' | 'number' | 'percentage'
): string => {
  switch (type) {
    case 'currency':
      return formatCurrency(value)
    case 'percentage':
      return `${value.toFixed(1)}%`
    case 'number':
    default:
      return Math.round(value).toString()
  }
}

/**
 * Calculate growth rate between two values
 */
export const calculateGrowthRate = (
  current: number,
  previous: number
): number => {
  if (previous === 0) return current > 0 ? 100 : 0
  return ((current - previous) / previous) * 100
}

/**
 * Get base chart options with theme support
 */
export const getBaseChartOptions = (theme: Theme): ApexCharts.ApexOptions => {
  const isDark = theme.palette.mode === 'dark'

  return {
    chart: {
      fontFamily: theme.typography.fontFamily,
      background: 'transparent',
      toolbar: {
        show: false,
      },
      zoom: {
        enabled: false,
      },
    },
    theme: {
      mode: isDark ? 'dark' : 'light',
    },
    grid: {
      borderColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      strokeDashArray: 3,
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      style: {
        fontSize: '12px',
      },
    },
    legend: {
      labels: {
        colors: isDark ? '#fff' : '#000',
      },
    },
    xaxis: {
      labels: {
        style: {
          colors: isDark ? '#aaa' : '#666',
          fontSize: '12px',
        },
      },
      axisBorder: {
        color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      },
      axisTicks: {
        color: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: isDark ? '#aaa' : '#666',
          fontSize: '12px',
        },
      },
    },
  }
}

/**
 * Format large currency values for chart labels (e.g., "R$ 10.5k")
 */
export const formatCompactCurrency = (value: number): string => {
  if (value >= 1000000) {
    return `R$ ${(value / 1000000).toFixed(1)}M`
  }
  if (value >= 1000) {
    return `R$ ${(value / 1000).toFixed(1)}k`
  }
  return formatCurrency(value)
}

/**
 * Get trend indicator (up/down arrow) based on growth rate
 */
export const getTrendIndicator = (growthRate: number): string => {
  if (growthRate > 0) return '↑'
  if (growthRate < 0) return '↓'
  return '→'
}

/**
 * Get trend color based on growth rate
 */
export const getTrendColor = (growthRate: number, theme: Theme): string => {
  if (growthRate > 0) return theme.palette.success.main
  if (growthRate < 0) return theme.palette.error.main
  return theme.palette.text.secondary
}
