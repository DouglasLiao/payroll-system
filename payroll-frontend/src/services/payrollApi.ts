/**
 * payrollApi.ts — API calls for Payroll domain
 *
 * Follows the pattern from django-react-cms: one file per resource domain.
 * Each file imports from the shared axios instance in api.ts.
 */

import api from './api'
import type {
  Payroll,
  PayrollDetail,
  PayrollCreateData,
  PaginatedResponse,
} from '../types'

export interface PayrollFilters {
  status?: string
  reference_month?: string
  provider?: number
  page?: number
  page_size?: number
}

export interface PayrollStats {
  total: number
  draft: number
  paid: number
}

export const getPayrolls = async (
  params?: PayrollFilters
): Promise<PaginatedResponse<Payroll>> => {
  const searchParams = new URLSearchParams()

  if (params?.status && params.status !== 'all') {
    searchParams.append('status', params.status)
  }
  if (params?.reference_month) {
    // Convert from YYYY-MM (HTML5 month input) to MM/YYYY (backend format)
    const [year, month] = params.reference_month.split('-')
    const formattedMonth = `${month}/${year}`
    searchParams.append('reference_month', formattedMonth)
  }
  if (params?.provider) {
    searchParams.append('provider', params.provider.toString())
  }
  if (params?.page) {
    searchParams.append('page', params.page.toString())
  }
  if (params?.page_size) {
    searchParams.append('page_size', params.page_size.toString())
  }

  const queryString = searchParams.toString()
  const url = `/payrolls/${queryString ? '?' + queryString : ''}`

  const { data } = await api.get<PaginatedResponse<Payroll>>(url)
  return data
}

export const getPayrollStats = async (): Promise<PayrollStats> => {
  const { data } = await api.get<PayrollStats>('/payrolls/stats/')
  return data
}

export const getPayrollDetail = async (id: number): Promise<PayrollDetail> => {
  const { data } = await api.get<PayrollDetail>(`/payrolls/${id}/`)
  return data
}

export const createPayroll = async (
  payrollData: PayrollCreateData
): Promise<PayrollDetail> => {
  const { data } = await api.post<PayrollDetail>(
    '/payrolls/calculate/',
    payrollData
  )
  return data
}

export const updatePayroll = async (
  id: number,
  updates: Partial<PayrollCreateData>
): Promise<PayrollDetail> => {
  const { data } = await api.patch<PayrollDetail>(`/payrolls/${id}/`, updates)
  return data
}

export const closePayroll = async (id: number): Promise<PayrollDetail> => {
  const { data } = await api.post<PayrollDetail>(`/payrolls/${id}/close/`)
  return data
}

export const markPayrollAsPaid = async (id: number): Promise<PayrollDetail> => {
  const { data } = await api.post<PayrollDetail>(
    `/payrolls/${id}/mark-as-paid/`
  )
  return data
}

export const reopenPayroll = async (id: number): Promise<PayrollDetail> => {
  const { data } = await api.post<PayrollDetail>(`/payrolls/${id}/reopen/`)
  return data
}

export const recalculatePayroll = async (
  id: number,
  updates: Partial<PayrollCreateData>
): Promise<PayrollDetail> => {
  const { data } = await api.put<PayrollDetail>(
    `/payrolls/${id}/recalculate/`,
    updates
  )
  return data
}

export const downloadPayrollFile = async (payrollId: number): Promise<void> => {
  const response = await api.get(`/payrolls/${payrollId}/export-file/`, {
    responseType: 'blob',
  })

  const contentDisposition =
    response.headers['content-disposition'] ||
    response.headers['Content-Disposition']

  let filename = `folha_${payrollId}.xlsx`

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/)
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1]
    }
  }

  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
