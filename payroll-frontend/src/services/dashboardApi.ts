/**
 * dashboardApi.ts — API calls for Dashboard and Reports domain
 */

import api from 'src/services/api'
import type { EnhancedDashboardStats } from 'src/types'

export interface DashboardFilters {
  period?: '7d' | '30d' | '90d' | '1y' | 'all'
  start_date?: string
  end_date?: string
}

export const getDashboardStats = async (
  filters?: DashboardFilters
): Promise<EnhancedDashboardStats> => {
  const params = new URLSearchParams()
  if (filters?.period) params.append('period', filters.period)
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)

  const queryString = params.toString()
  const url = `/dashboard/${queryString ? '?' + queryString : ''}`

  const { data } = await api.get<EnhancedDashboardStats>(url)
  return data
}

export const downloadMonthlyReport = async (
  referenceMonth: string
): Promise<void> => {
  // Direct navigation to leverage browser's native download handling.
  // Authentication is handled via Cookies sent automatically.
  const url = `${api.defaults.baseURL}payrolls/monthly-report/?reference_month=${referenceMonth}`
  window.location.href = url
}

export const sendReportEmail = async (
  referenceMonth: string,
  email?: string
) => {
  const { data } = await api.post('/payrolls/email-report/', {
    reference_month: referenceMonth,
    email,
  })
  return data
}
