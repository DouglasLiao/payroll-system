import type { Theme } from '@mui/material'
import { formatCurrency } from 'src/utils/formatters'

/**
 * Get chart colors optimized for both light and dark modes
 */
export const getChartColors = (theme: Theme) => {
  return {
    draft: theme.palette.warning.main, // Orange
    closed: theme.palette.info.main, // Blue
    paid: theme.palette.success.main, // Green
    total: theme.palette.secondary.main, // Primary or Secondary
    income: theme.palette.info.light, // Cyanish
    expense: theme.palette.error.main, // Red
    balance: theme.palette.success.light, // Light Green
    projection: theme.palette.text.secondary, // Grey
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
      borderColor: theme.palette.divider,
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
        colors: theme.palette.text.primary,
      },
    },
    xaxis: {
      labels: {
        style: {
          colors: theme.palette.text.secondary,
          fontSize: '12px',
        },
      },
      axisBorder: {
        color: theme.palette.divider,
      },
      axisTicks: {
        color: theme.palette.divider,
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: theme.palette.text.secondary,
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
