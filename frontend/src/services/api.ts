import axios from 'axios'
import type { Provider, Payment, DashboardStats } from '../types'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

export const getProviders = async () => {
  const { data } = await api.get<Provider[]>('/providers/')
  return data
}

export const createProvider = async (provider: Omit<Provider, 'id'>) => {
  const { data } = await api.post<Provider>('/providers/', provider)
  return data
}

export const updateProvider = async (id: number, provider: Partial<Provider>) => {
  const { data } = await api.patch<Provider>(`/providers/${id}/`, provider)
  return data
}

export const deleteProvider = async (id: number) => {
  await api.delete(`/providers/${id}/`)
}

export const getPayments = async () => {
  const { data } = await api.get<Payment[]>('/payments/')
  return data
}

export const createPayment = async (payment: Omit<Payment, 'id' | 'total_calculated'>) => {
  const { data } = await api.post<Payment>('/payments/', payment)
  return data
}

export const payPayment = async (id: number) => {
  const { data } = await api.post<Payment>(`/payments/${id}/pay/`)
  return data
}

export const getDashboardStats = async () => {
  const { data } = await api.get<DashboardStats>('/dashboard/')
  return data
}

export default api
