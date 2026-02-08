import api from './api'
import type {
  Company,
  PayrollMathTemplate,
  PayrollConfiguration,
  Subscription,
  SuperAdminStats,
  PaginatedResponse,
} from '../types'

// ==================== STATS ====================

export const getSuperAdminStats = async () => {
  const { data } = await api.get<SuperAdminStats>('/super-admin/stats/')
  return data
}

// ==================== COMPANIES ====================

export interface CompanyFilters {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
}

export const getCompanies = async (params?: CompanyFilters) => {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.append('page', params.page.toString())
  if (params?.page_size)
    searchParams.append('page_size', params.page_size.toString())
  if (params?.search) searchParams.append('search', params.search)
  if (params?.is_active !== undefined)
    searchParams.append('is_active', params.is_active.toString())

  const queryString = searchParams.toString()
  const url = `/companies/${queryString ? '?' + queryString : ''}`

  const { data } = await api.get<PaginatedResponse<Company>>(url)
  return data
}

export const getCompany = async (id: number) => {
  const { data } = await api.get<Company>(`/companies/${id}/`)
  return data
}

export const createCompany = async (company: Partial<Company>) => {
  const { data } = await api.post<Company>('/companies/', company)
  return data
}

export const updateCompany = async (id: number, company: Partial<Company>) => {
  const { data } = await api.patch<Company>(`/companies/${id}/`, company)
  return data
}

export const approveCompany = async (id: number) => {
  const { data } = await api.post<{ message: string }>(
    `/companies/${id}/approve/`
  )
  return data
}

// ==================== CONFIGURATIONS ====================

export const getPayrollConfig = async (companyId: number) => {
  const { data } = await api.get<PayrollConfiguration[]>(
    `/payroll-configs/?company_id=${companyId}`
  )
  return data[0] // Assuming 1:1, usually returns list
}

export const updatePayrollConfig = async (
  configId: number,
  config: Partial<PayrollConfiguration>
) => {
  const { data } = await api.patch<PayrollConfiguration>(
    `/payroll-configs/${configId}/`,
    config
  )
  return data
}

export const applyTemplateToCompany = async (
  companyId: number,
  templateId: number
) => {
  const { data } = await api.post<PayrollConfiguration>(
    '/payroll-configs/apply-template/',
    {
      company_id: companyId,
      template_id: templateId,
    }
  )
  return data
}

// ==================== TEMPLATES ====================

export const getMathTemplates = async () => {
  const { data } =
    await api.get<PaginatedResponse<PayrollMathTemplate>>('/math-templates/')
  return data.results // Assuming pagination or list
}

export const createMathTemplate = async (
  template: Partial<PayrollMathTemplate>
) => {
  const { data } = await api.post<PayrollMathTemplate>(
    '/math-templates/',
    template
  )
  return data
}

export const updateMathTemplate = async (
  id: number,
  template: Partial<PayrollMathTemplate>
) => {
  const { data } = await api.patch<PayrollMathTemplate>(
    `/math-templates/${id}/`,
    template
  )
  return data
}

export const deleteMathTemplate = async (id: number) => {
  await api.delete(`/math-templates/${id}/`)
}

// ==================== SUBSCRIPTIONS ====================

export const getSubscription = async (companyId: number) => {
  const { data } = await api.get<PaginatedResponse<Subscription>>(
    `/subscriptions/?company_id=${companyId}`
  )
  return data.results[0]
}

export const getAllSubscriptions = async (page = 1) => {
  const { data } = await api.get<PaginatedResponse<Subscription>>(
    `/subscriptions/?page=${page}`
  )
  return data
}

export const renewSubscription = async (
  subscriptionId: number,
  planType?: string,
  endDate?: string
) => {
  const { data } = await api.post<Subscription>(
    `/subscriptions/${subscriptionId}/renew/`,
    {
      plan_type: planType,
      end_date: endDate,
    }
  )
  return data
}
