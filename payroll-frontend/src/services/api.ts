/**
 * api.ts — Shared Axios instance + re-exports for backward compatibility
 *
 * This file now serves two purposes:
 * 1. Exports the shared axios instance used by all domain API files
 * 2. Re-exports all functions from domain-specific files so existing imports
 *    continue to work without changes (backward compatibility)
 *
 * New code should import directly from the domain files:
 *   import { getPayrolls } from './payrollApi'
 *   import { getProviders } from './providerApi'
 *   import { getDashboardStats } from './dashboardApi'
 */

import axios from 'axios'

// Get API base URL from environment variables
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Enable sending cookies (JWT tokens) with requests
})

export default api

// ── Re-exports for backward compatibility ─────────────────────────────────────

export type { ProviderFilters } from './providerApi'
export {
  getProviders,
  createProvider,
  updateProvider,
  deleteProvider,
} from './providerApi'

export type { PayrollFilters, PayrollStats } from './payrollApi'
export {
  getPayrolls,
  getPayrollStats,
  getPayrollDetail,
  createPayroll,
  updatePayroll,
  closePayroll,
  markPayrollAsPaid,
  reopenPayroll,
  recalculatePayroll,
  downloadPayrollFile,
} from './payrollApi'

export type { DashboardFilters } from './dashboardApi'
export {
  getDashboardStats,
  downloadMonthlyReport,
  sendReportEmail,
} from './dashboardApi'

// ── Legacy: Payments (kept here since not yet extracted) ──────────────────────

import type { Payment, PaginatedResponse } from '../types'

export const getPayments = async () => {
  const { data } = await api.get<PaginatedResponse<Payment>>('/payments/')
  return data.results
}

export const createPayment = async (
  payment: Omit<Payment, 'id' | 'total_calculated'>
) => {
  const { data } = await api.post<Payment>('/payments/', payment)
  return data
}

export const payPayment = async (id: number) => {
  const { data } = await api.post<Payment>(`/payments/${id}/pay/`)
  return data
}
