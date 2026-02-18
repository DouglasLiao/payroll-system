/**
 * providerApi.ts — API calls for Provider domain
 */

import api from 'src/services/api'
import type { Provider, PaginatedResponse } from 'src/types'

export interface ProviderFilters {
  page?: number
  page_size?: number
  search?: string
}

export const getProviders = async (
  params?: ProviderFilters
): Promise<PaginatedResponse<Provider>> => {
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

export const createProvider = async (
  provider: Omit<Provider, 'id'>
): Promise<Provider> => {
  const { data } = await api.post<Provider>('/providers/', provider)
  return data
}

export const updateProvider = async (
  id: number,
  provider: Partial<Provider>
): Promise<Provider> => {
  const { data } = await api.patch<Provider>(`/providers/${id}/`, provider)
  return data
}

export const deleteProvider = async (id: number): Promise<void> => {
  await api.delete(`/providers/${id}/`)
}
