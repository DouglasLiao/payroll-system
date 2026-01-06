import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { CssBaseline } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SnackbarProvider } from 'notistack'
import { ThemeContextProvider } from './contexts/ThemeContext'

// Layouts & Pages (Placeholders for now)
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Providers from './pages/Providers'
import Payments from './pages/Payments'
// const EmployeeView = () => <div>Employee View</div>; // Still placeholder for now
const EmployeeView = () => <div>Employee View (Coming Soon)</div>

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeContextProvider>
        <CssBaseline />
        <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
          <BrowserRouter>
            <Routes>
              {/* Admin Routes with Sidebar */}
              <Route path="/" element={<MainLayout />}>
                <Route index element={<Dashboard />} />
                <Route path="admin/providers" element={<Providers />} />
                <Route path="admin/payments" element={<Payments />} />
              </Route>

              {/* Standalone Employee Route */}
              <Route path="/employee/:id" element={<EmployeeView />} />

              {/* Catch all */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </BrowserRouter>
        </SnackbarProvider>
      </ThemeContextProvider>
    </QueryClientProvider>
  )
}

export default App
