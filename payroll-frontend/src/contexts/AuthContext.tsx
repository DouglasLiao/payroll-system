import React, {
  createContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
} from 'react'
import { authApi, type User } from '../services/authApi'

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<User>
  logout: () => Promise<void>
  isAuthenticated: boolean
  isLoading: boolean
  inactivityTimeout: number
  updateTimeout: (timeout: number) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [inactivityTimeout, setInactivityTimeout] = useState(300)
  const inactivityTimerRef = useRef<number | null>(null)
  const lastActivityRef = useRef<number>(Date.now())

  // Resetar timer de inatividade
  const resetInactivityTimer = useCallback(() => {
    lastActivityRef.current = Date.now()

    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current)
    }

    inactivityTimerRef.current = setTimeout(() => {
      // Logout automático por inatividade
      console.log('Sessão expirada por inatividade')
      logout()
    }, inactivityTimeout * 1000)
  }, [inactivityTimeout])

  // Monitorar atividade do usuário
  useEffect(() => {
    if (!user) return

    const events = ['mousedown', 'keydown', 'scroll', 'touchstart']

    const handleActivity = () => {
      resetInactivityTimer()
    }

    events.forEach((event) => {
      document.addEventListener(event, handleActivity)
    })

    // Iniciar timer
    resetInactivityTimer()

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handleActivity)
      })
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current)
      }
    }
  }, [user, resetInactivityTimer])

  // Carregar usuário ao montar (verifica cookies)
  useEffect(() => {
    const loadUser = async () => {
      try {
        const userData = await authApi.getCurrentUser()
        setUser(userData)
        setInactivityTimeout(userData.inactivity_timeout || 300)
      } catch {
        // Sem sessão ativa
        console.log('Nenhuma sessão ativa')
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
  }, [])

  const login = async (username: string, password: string) => {
    // Limpar flag de redirecionamento
    sessionStorage.removeItem('auth_redirect')
    const data = await authApi.login(username, password)
    setUser(data.user)
    setInactivityTimeout(data.user.inactivity_timeout || 300)
    return data.user
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Erro ao fazer logout:', error)
    } finally {
      setUser(null)
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current)
      }
      window.location.href = '/login'
    }
  }

  const updateTimeout = async (timeout: number) => {
    await authApi.updateTimeout(timeout)
    setInactivityTimeout(timeout)
    if (user) {
      setUser({ ...user, inactivity_timeout: timeout })
    }
  }

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isLoading,
    inactivityTimeout,
    updateTimeout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
