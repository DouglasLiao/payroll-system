import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { CssBaseline, ThemeProvider } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SnackbarProvider } from 'notistack'
import { ThemeContextProvider } from './contexts/ThemeContext'
import { AuthProvider } from './contexts/AuthContext'
import { getTheme } from './theme'
import 'dayjs/locale/pt-br'

// Layouts & Pages
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Providers from './pages/Providers'
import Payrolls from './pages/Payrolls'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import UnauthorizedPage from './pages/UnauthorizedPage'
import SuperAdminDashboard from './pages/SuperAdminDashboard'
import ProviderPayments from './pages/ProviderPayments'
import ProtectedRoute from './components/ProtectedRoute'
const EmployeeView = () => <div>Employee View (Coming Soon)</div>

const queryClient = new QueryClient()

// Fixed light theme for login page
const loginTheme = getTheme('light')

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Routes - Auth pages with fixed light theme */}
              <Route
                path="/login"
                element={
                  <ThemeProvider theme={loginTheme}>
                    <CssBaseline />
                    <LoginPage />
                  </ThemeProvider>
                }
              />
              <Route
                path="/register"
                element={
                  <ThemeProvider theme={loginTheme}>
                    <CssBaseline />
                    <RegisterPage />
                  </ThemeProvider>
                }
              />
              <Route
                path="/forgot-password"
                element={
                  <ThemeProvider theme={loginTheme}>
                    <CssBaseline />
                    <ForgotPasswordPage />
                  </ThemeProvider>
                }
              />
              <Route
                path="/reset-password"
                element={
                  <ThemeProvider theme={loginTheme}>
                    <CssBaseline />
                    <ResetPasswordPage />
                  </ThemeProvider>
                }
              />

              {/* All other routes with dynamic theme */}
              <Route
                path="/*"
                element={
                  <ThemeContextProvider>
                    <CssBaseline />
                    <Routes>
                      <Route
                        path="/unauthorized"
                        element={<UnauthorizedPage />}
                      />

                      {/* Super Admin Routes */}
                      <Route
                        path="/super-admin"
                        element={
                          <ProtectedRoute allowedRoles={['SUPER_ADMIN']}>
                            <MainLayout />
                          </ProtectedRoute>
                        }
                      >
                        <Route index element={<SuperAdminDashboard />} />
                      </Route>

                      {/* Protected Admin Routes with Sidebar */}
                      <Route
                        path="/"
                        element={
                          <ProtectedRoute allowedRoles={['CUSTOMER_ADMIN']}>
                            <MainLayout />
                          </ProtectedRoute>
                        }
                      >
                        <Route index element={<Dashboard />} />
                        <Route path="admin/providers" element={<Providers />} />
                        <Route path="admin/payrolls" element={<Payrolls />} />
                      </Route>

                      {/* Provider Routes */}
                      <Route
                        path="/provider"
                        element={
                          <ProtectedRoute allowedRoles={['PROVIDER']}>
                            <MainLayout />
                          </ProtectedRoute>
                        }
                      >
                        <Route index element={<ProviderPayments />} />
                      </Route>

                      {/* Standalone Employee Route - Provider */}
                      <Route
                        path="/employee/:id"
                        element={
                          <ProtectedRoute allowedRoles={['PROVIDER']}>
                            <EmployeeView />
                          </ProtectedRoute>
                        }
                      />

                      {/* Catch all */}
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </ThemeContextProvider>
                }
              />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </SnackbarProvider>
    </QueryClientProvider>
  )
}

export default App
