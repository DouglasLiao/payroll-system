import axios, { AxiosError } from 'axios'

/**
 * authApi.ts — Authentication & Registration API
 *
 * All routes are under /users/auth/ (moved from /auth/ in the users/ app refactor).
 */

const authAxios = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// ── Types ─────────────────────────────────────────────────────────────────────

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: 'SUPER_ADMIN' | 'CUSTOMER_ADMIN' | 'PROVIDER'
  role_display: string
  company: number | null
  company_name: string | null
  company_cnpj?: string | null
  inactivity_timeout: number
  created_at: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

// ── Auth API ──────────────────────────────────────────────────────────────────

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const { data } = await authAxios.post<LoginResponse>('/users/auth/token/', {
      username,
      password,
    })
    return data
  },

  getCurrentUser: async (): Promise<User> => {
    const { data } = await authAxios.get<User>('/users/auth/me/')
    return data
  },

  logout: async (): Promise<void> => {
    await authAxios.post('/users/auth/logout/')
  },

  updateTimeout: async (
    timeout: number
  ): Promise<{ message: string; timeout: number }> => {
    const { data } = await authAxios.post('/users/auth/update-timeout/', {
      timeout,
    })
    return data
  },

  changePassword: async (
    oldPassword: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    const { data } = await authAxios.post('/users/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return data
  },

  requestPasswordReset: async (email: string): Promise<{ message: string }> => {
    const { data } = await authAxios.post(
      '/users/auth/password-reset/request/',
      { email }
    )
    return data
  },

  confirmPasswordReset: async (
    token: string,
    newPassword: string,
    confirmPassword: string
  ): Promise<{ message: string }> => {
    const { data } = await authAxios.post(
      '/users/auth/password-reset/confirm/',
      {
        token,
        new_password: newPassword,
        new_password_confirm: confirmPassword,
      }
    )
    return data
  },

  checkEmail: async (
    email: string
  ): Promise<{ email: string; exists: boolean; available: boolean }> => {
    const { data } = await authAxios.post('/users/auth/check-email/', { email })
    return data
  },

  register: async (data: {
    email: string
    username: string
    password: string
    password_confirm: string
    first_name?: string
    last_name?: string
    company_name: string
    company_cnpj: string
    company_phone?: string
  }): Promise<{ message: string; user: User }> => {
    const { data: response } = await authAxios.post(
      '/users/auth/register/',
      data
    )
    return response
  },
}

// ── Interceptor ───────────────────────────────────────────────────────────────

authAxios.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (
      error.response?.status === 401 &&
      !window.location.pathname.includes('/login')
    ) {
      const alreadyRedirected = sessionStorage.getItem('auth_redirect')
      if (!alreadyRedirected) {
        sessionStorage.setItem('auth_redirect', 'true')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default authAxios
