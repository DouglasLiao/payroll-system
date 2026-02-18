import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { CssBaseline, ThemeProvider } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SnackbarProvider } from 'notistack'
import { ThemeContextProvider } from 'src/contexts/ThemeContext'
import { AuthProvider } from 'src/contexts/AuthContext'
import { getTheme } from 'src/theme'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'

// Layouts & Pages
// Layouts & Pages
import MainLayout from 'src/layouts/MainLayout'
import Dashboard from 'src/pages/customer-admin/Dashboard'
import Providers from 'src/pages/customer-admin/Providers'
import Payrolls from 'src/pages/customer-admin/Payrolls'
import Reports from 'src/pages/customer-admin/Reports'
import Settings from 'src/pages/customer-admin/Settings'
import LoginPage from 'src/pages/LoginPage'
import RegisterPage from 'src/pages/RegisterPage'
import ForgotPasswordPage from 'src/pages/ForgotPasswordPage'
import ResetPasswordPage from 'src/pages/ResetPasswordPage'
import UnauthorizedPage from 'src/pages/UnauthorizedPage'
import SuperAdminOverview from 'src/pages/super-admin/Overview'
import SuperAdminCompanies from 'src/pages/super-admin/Companies'
import CompanyConfig from 'src/pages/super-admin/CompanyConfig'
import CompanySubscription from 'src/pages/super-admin/CompanySubscription'
import SuperAdminApprovals from 'src/pages/super-admin/Approvals'
import SuperAdminSubscriptions from 'src/pages/super-admin/Subscriptions'
import MathTemplateManager from 'src/pages/super-admin/MathTemplateManager'
import ProviderPayments from 'src/pages/provider/ProviderPayments'
import { ProtectedRoute } from 'src/components/routing'
const EmployeeView = () => <div>Employee View (Coming Soon)</div>

const queryClient = new QueryClient()

// Configure dayjs to use Brazilian Portuguese locale globally
dayjs.locale('pt-br')

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
                        <Route
                          index
                          element={<Navigate to="dashboard" replace />}
                        />
                        <Route
                          path="dashboard"
                          element={<SuperAdminOverview />}
                        />
                        <Route
                          path="companies"
                          element={<SuperAdminCompanies />}
                        />
                        <Route
                          path="companies/:id/config"
                          element={<CompanyConfig />}
                        />
                        <Route
                          path="companies/:id/subscription"
                          element={<CompanySubscription />}
                        />
                        <Route
                          path="approvals"
                          element={<SuperAdminApprovals />}
                        />
                        <Route
                          path="subscriptions"
                          element={<SuperAdminSubscriptions />}
                        />
                        <Route
                          path="configs"
                          element={<MathTemplateManager />}
                        />
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
                        <Route path="admin/reports" element={<Reports />} />
                        <Route path="admin/settings" element={<Settings />} />
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
