import type {
  Payroll,
  PayrollStats,
  MonthlyData,
  FinancialMetrics,
} from '../types'

/**
 * Calculate aggregate statistics from payroll data
 */
export const calculatePayrollStats = (payrolls: Payroll[]): PayrollStats => {
  const stats: PayrollStats = {
    total: payrolls.length,
    drafts: 0,
    closed: 0,
    paid: 0,
    totalValue: 0,
    avgValue: 0,
  }

  payrolls.forEach((payroll) => {
    const value = parseFloat(payroll.net_value)
    stats.totalValue += value

    switch (payroll.status) {
      case 'DRAFT':
        stats.drafts++
        break
      case 'CLOSED':
        stats.closed++
        break
      case 'PAID':
        stats.paid++
        break
    }
  })

  stats.avgValue = payrolls.length > 0 ? stats.totalValue / payrolls.length : 0

  return stats
}

/**
 * Aggregate payroll data by month
 */
export const aggregateMonthlyData = (payrolls: Payroll[]): MonthlyData => {
  const monthlyData: MonthlyData = {}

  payrolls.forEach((payroll) => {
    const month = payroll.reference_month

    if (!monthlyData[month]) {
      monthlyData[month] = {
        draft: 0,
        closed: 0,
        paid: 0,
        total: 0,
        draftValue: 0,
        closedValue: 0,
        paidValue: 0,
      }
    }

    const value = parseFloat(payroll.net_value)
    monthlyData[month].total += value

    const status = payroll.status.toLowerCase() as 'draft' | 'closed' | 'paid'
    monthlyData[month][status]++
    monthlyData[month][
      `${status}Value` as 'draftValue' | 'closedValue' | 'paidValue'
    ] += value
  })

  return monthlyData
}

/**
 * Sort months in MM/YYYY format chronologically
 * Converts MM/YYYY to YYYY-MM for sorting, then returns sorted MM/YYYY
 */
export const sortMonthsChronologically = (months: string[]): string[] => {
  return months.sort((a, b) => {
    // Convert MM/YYYY to YYYY-MM for proper date comparison
    const [monthA, yearA] = a.split('/')
    const [monthB, yearB] = b.split('/')
    const dateA = `${yearA}-${monthA.padStart(2, '0')}`
    const dateB = `${yearB}-${monthB.padStart(2, '0')}`
    return dateA.localeCompare(dateB)
  })
}

/**
 * Calculate financial metrics from monthly data
 */
export const calculateFinancialMetrics = (
  monthlyData: MonthlyData,
  payrolls: Payroll[]
): FinancialMetrics => {
  const allMonths = Object.keys(monthlyData)
  const months = sortMonthsChronologically(allMonths)
  const monthlyValues = months.map((m) => monthlyData[m].total)

  // Calculate average monthly value
  const avgMonthlyValue =
    monthlyValues.length > 0
      ? monthlyValues.reduce((sum, val) => sum + val, 0) / monthlyValues.length
      : 0

  // Calculate growth rate (last month vs previous month)
  let monthlyGrowth = 0
  if (monthlyValues.length >= 2) {
    const lastMonth = monthlyValues[monthlyValues.length - 1]
    const previousMonth = monthlyValues[monthlyValues.length - 2]
    if (previousMonth !== 0) {
      monthlyGrowth = ((lastMonth - previousMonth) / previousMonth) * 100
    }
  }

  // Calculate totals by status
  const totalPending = payrolls
    .filter((p) => p.status === 'CLOSED')
    .reduce((sum, p) => sum + parseFloat(p.net_value), 0)

  const totalPaid = payrolls
    .filter((p) => p.status === 'PAID')
    .reduce((sum, p) => sum + parseFloat(p.net_value), 0)

  // Simple projection based on average
  const projectedNextMonth = avgMonthlyValue

  // Cash flow (paid - pending)
  const cashFlow = totalPaid - totalPending

  return {
    monthlyGrowth,
    avgMonthlyValue,
    projectedNextMonth,
    totalPending,
    totalPaid,
    cashFlow,
  }
}

/**
 * Project next month's value based on historical data
 * Uses simple moving average for projection
 */
export const projectNextMonth = (monthlyData: MonthlyData): number => {
  const allMonths = Object.keys(monthlyData)
  const months = sortMonthsChronologically(allMonths)
  const last3Months = months.slice(-3)

  if (last3Months.length === 0) return 0

  const sum = last3Months.reduce(
    (acc, month) => acc + monthlyData[month].total,
    0
  )
  return sum / last3Months.length
}
/**
 * Get list of last N months in MM/YYYY format
 * Returns months in chronological order (oldest to newest)
 */
export const getLastNMonths = (n: number): string[] => {
  const months: string[] = []
  const today = new Date()

  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(today.getFullYear(), today.getMonth() - i, 1)
    const month = (d.getMonth() + 1).toString().padStart(2, '0')
    const year = d.getFullYear()
    months.push(`${month}/${year}`)
  }

  return months
}
