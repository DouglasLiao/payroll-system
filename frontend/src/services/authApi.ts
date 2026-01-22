import axios, { AxiosError } from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true, // Importante para enviar cookies httpOnly
  headers: {
    'Content-Type': 'application/json',
  },
})

// Tipos
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

// API de Autenticação
export const authApi = {
  /**
   * Login do usuário
   * Cookies são definidos automaticamente pelo backend
   */
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login/', {
      username,
      password,
    })
    return response.data
  },

  /**
   * Busca informações do usuário logado
   * Token é enviado automaticamente via cookie
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me/')
    return response.data
  },

  /**
   * Logout do usuário
   * Backend remove os cookies
   */
  logout: async (): Promise<void> => {
    await api.post('/auth/logout/')
  },

  /**
   * Atualiza timeout de inatividade do usuário
   */
  updateTimeout: async (
    timeout: number
  ): Promise<{ message: string; timeout: number }> => {
    const response = await api.post('/auth/update-timeout/', { timeout })
    return response.data
  },

  /**
   * Altera senha do usuário
   */
  changePassword: async (
    oldPassword: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    const response = await api.post('/auth/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
    })
    return response.data
  },
}

// Interceptor para lidar com erros de autenticação
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Apenas redirecionar para login se não estiver na página de login
    // e se for erro de autenticação real
    if (
      error.response?.status === 401 &&
      !window.location.pathname.includes('/login')
    ) {
      // Evitar loops - só redirecionar uma vez
      const alreadyRedirected = sessionStorage.getItem('auth_redirect')
      if (!alreadyRedirected) {
        sessionStorage.setItem('auth_redirect', 'true')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
