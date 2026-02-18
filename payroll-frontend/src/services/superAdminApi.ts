/**
 * superAdminApi.ts — Super Admin API (companies, subscriptions, templates, config)
 *
 * All routes are under /users/ (moved from root in the users/ app refactor).
 */

import api from 'src/services/api'
import type {
  Company,
  PayrollMathTemplate,
  PayrollConfiguration,
  Subscription,
  SuperAdminStats,
  PaginatedResponse,
} from 'src/types'

// ── Stats ─────────────────────────────────────────────────────────────────────

export const getSuperAdminStats = async () => {
  const { data } = await api.get<SuperAdminStats>('/users/super-admin/stats/')
  return data
}

// ── Companies ─────────────────────────────────────────────────────────────────

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
  const url = `/users/companies/${queryString ? '?' + queryString : ''}`

  const { data } = await api.get<PaginatedResponse<Company>>(url)
  return data
}

export const getCompany = async (id: number) => {
  const { data } = await api.get<Company>(`/users/companies/${id}/`)
  return data
}

export const createCompany = async (company: Partial<Company>) => {
  const { data } = await api.post<Company>('/users/companies/', company)
  return data
}

export const updateCompany = async (id: number, company: Partial<Company>) => {
  const { data } = await api.patch<Company>(`/users/companies/${id}/`, company)
  return data
}

export const approveCompany = async (id: number) => {
  const { data } = await api.post<{ message: string }>(
    `/users/companies/${id}/approve/`
  )
  return data
}

export const rejectCompany = async (id: number) => {
  const { data } = await api.post<{ message: string }>(
    `/users/companies/${id}/reject/`
  )
  return data
}

export const toggleCompanyStatus = async (id: number) => {
  const { data } = await api.post<{ message: string; is_active: boolean }>(
    `/users/companies/${id}/toggle-status/`
  )
  return data
}

// ── Payroll Config ────────────────────────────────────────────────────────────

export const getPayrollConfig = async (companyId: number) => {
  const { data } = await api.get<PayrollConfiguration[]>(
    `/users/payroll-configs/?company_id=${companyId}`
  )
  return data[0]
}

export const updatePayrollConfig = async (
  configId: number,
  config: Partial<PayrollConfiguration>
) => {
  const { data } = await api.patch<PayrollConfiguration>(
    `/users/payroll-configs/${configId}/`,
    config
  )
  return data
}

export const applyTemplateToCompany = async (
  companyId: number,
  templateId: number
) => {
  const { data } = await api.post<PayrollConfiguration>(
    '/users/payroll-configs/apply-template/',
    {
      company_id: companyId,
      template_id: templateId,
    }
  )
  return data
}

// ── Math Templates ────────────────────────────────────────────────────────────

export const getMathTemplates = async () => {
  const { data } = await api.get<PaginatedResponse<PayrollMathTemplate>>(
    '/users/math-templates/'
  )
  return data.results
}

export const createMathTemplate = async (
  template: Partial<PayrollMathTemplate>
) => {
  const { data } = await api.post<PayrollMathTemplate>(
    '/users/math-templates/',
    template
  )
  return data
}

export const updateMathTemplate = async (
  id: number,
  template: Partial<PayrollMathTemplate>
) => {
  const { data } = await api.patch<PayrollMathTemplate>(
    `/users/math-templates/${id}/`,
    template
  )
  return data
}

export const deleteMathTemplate = async (id: number) => {
  await api.delete(`/users/math-templates/${id}/`)
}

// ── Subscriptions ─────────────────────────────────────────────────────────────

export const getSubscription = async (companyId: number) => {
  const { data } = await api.get<PaginatedResponse<Subscription>>(
    `/users/subscriptions/?company_id=${companyId}`
  )
  return data.results[0]
}

export const getAllSubscriptions = async (page = 1) => {
  const { data } = await api.get<PaginatedResponse<Subscription>>(
    `/users/subscriptions/?page=${page}`
  )
  return data
}

export const renewSubscription = async (
  subscriptionId: number,
  planType?: string,
  endDate?: string
) => {
  const { data } = await api.post<Subscription>(
    `/users/subscriptions/${subscriptionId}/renew/`,
    {
      plan_type: planType,
      end_date: endDate,
    }
  )
  return data
}
