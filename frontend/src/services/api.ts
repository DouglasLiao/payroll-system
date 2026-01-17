import axios from 'axios'
import type {
  Provider,
  Payment,
  DashboardStats,
  PaginatedResponse,
  Payroll,
  PayrollDetail,
  PayrollCreateData,
} from '../types'

// Get API base URL from environment variables
// Fallback to localhost for development if not set
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// ==================== PROVIDERS ====================

export interface ProviderFilters {
  page?: number
  page_size?: number
}

export const getProviders = async (params?: ProviderFilters) => {
  const searchParams = new URLSearchParams()

  if (params?.page) {
    searchParams.append('page', params.page.toString())
  }
  if (params?.page_size) {
    searchParams.append('page_size', params.page_size.toString())
  }

  const queryString = searchParams.toString()
  const url = `/providers/${queryString ? '?' + queryString : ''}`

  const { data } = await api.get<PaginatedResponse<Provider>>(url)
  return data
}

export const createProvider = async (provider: Omit<Provider, 'id'>) => {
  const { data } = await api.post<Provider>('/providers/', provider)
  return data
}

export const updateProvider = async (
  id: number,
  provider: Partial<Provider>
) => {
  const { data } = await api.patch<Provider>(`/providers/${id}/`, provider)
  return data
}

export const deleteProvider = async (id: number) => {
  await api.delete(`/providers/${id}/`)
}

// ==================== PAYMENTS (Legacy) ====================

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

// ==================== PAYROLLS ====================

export interface PayrollFilters {
  status?: string
  reference_month?: string
  provider?: number
  page?: number
  page_size?: number
}

export const getPayrolls = async (params?: PayrollFilters) => {
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

export const getPayrollDetail = async (id: number) => {
  const { data } = await api.get<PayrollDetail>(`/payrolls/${id}/`)
  return data
}

export const createPayroll = async (payrollData: PayrollCreateData) => {
  const { data } = await api.post<PayrollDetail>(
    '/payrolls/calculate/',
    payrollData
  )
  return data
}

export const closePayroll = async (id: number) => {
  const { data } = await api.post<Payroll>(`/payrolls/${id}/close/`)
  return data
}

export const markPayrollAsPaid = async (id: number) => {
  const { data } = await api.post<Payroll>(`/payrolls/${id}/mark-paid/`)
  return data
}

export const recalculatePayroll = async (
  id: number,
  updates: Partial<PayrollCreateData>
) => {
  const { data } = await api.put<PayrollDetail>(
    `/payrolls/${id}/recalculate/`,
    updates
  )
  return data
}

export const reopenPayroll = async (id: number) => {
  const { data } = await api.post<Payroll>(`/payrolls/${id}/reopen/`)
  return data
}

export const downloadPayrollExcel = async (
  payrollId: number
): Promise<void> => {
  const response = await api.get(`/payrolls/${payrollId}/export-excel/`, {
    responseType: 'blob',
  })

  // Extract filename from Content-Disposition header
  const contentDisposition = response.headers['content-disposition']
  const filename = contentDisposition
    ? contentDisposition.split('filename=')[1].replace(/"/g, '')
    : `folha_${payrollId}.xlsx`

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// ==================== DASHBOARD ====================

export const getDashboardStats = async () => {
  const { data } = await api.get<DashboardStats>('/dashboard/')
  return data
}

export default api
