import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getDashboardStats, getPayrolls, getProviders } from '../services/api'
import {
  calculatePayrollStats,
  aggregateMonthlyData,
  calculateFinancialMetrics,
} from '../utils/dashboardCalculations'
import type {
  PayrollStats,
  MonthlyData,
  FinancialMetrics,
  PaginatedResponse,
  Payroll,
  Provider,
  DashboardStats,
} from '../types'

interface UseDashboardDataReturn {
  payrollStats: PayrollStats
  monthlyData: MonthlyData
  financialMetrics: FinancialMetrics
  payrolls: PaginatedResponse<Payroll> | undefined
  providers: PaginatedResponse<Provider> | undefined
  dashboardData: DashboardStats | undefined
  isLoading: boolean
  error: Error | null
}

/**
 * Custom hook to centralize dashboard data fetching and calculations
 */
export const useDashboardData = (): UseDashboardDataReturn => {
  // Fetch dashboard stats
  const {
    data: dashboardData,
    isLoading: dashboardLoading,
    error: dashboardError,
  } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardStats,
  })

  // Fetch all payrolls for dashboard calculations
  const {
    data: payrolls,
    isLoading: payrollsLoading,
    error: payrollsError,
  } = useQuery({
    queryKey: ['payrolls-dashboard'],
    queryFn: () => getPayrolls({ page_size: 1000 }),
  })

  // Fetch providers
  const {
    data: providers,
    isLoading: providersLoading,
    error: providersError,
  } = useQuery({
    queryKey: ['providers-dashboard'],
    queryFn: () => getProviders({ page_size: 1000 }),
  })

  // Calculate payroll statistics
  const payrollStats = useMemo<PayrollStats>(() => {
    if (!payrolls?.results) {
      return {
        total: 0,
        drafts: 0,
        closed: 0,
        paid: 0,
        totalValue: 0,
        avgValue: 0,
      }
    }
    return calculatePayrollStats(payrolls.results)
  }, [payrolls])

  // Aggregate monthly data
  const monthlyData = useMemo<MonthlyData>(() => {
    if (!payrolls?.results) return {}
    return aggregateMonthlyData(payrolls.results)
  }, [payrolls])

  // Calculate financial metrics
  const financialMetrics = useMemo<FinancialMetrics>(() => {
    if (!payrolls?.results) {
      return {
        monthlyGrowth: 0,
        avgMonthlyValue: 0,
        projectedNextMonth: 0,
        totalPending: 0,
        totalPaid: 0,
        cashFlow: 0,
      }
    }
    return calculateFinancialMetrics(monthlyData, payrolls.results)
  }, [monthlyData, payrolls])

  const isLoading = dashboardLoading || payrollsLoading || providersLoading
  const error = (dashboardError ||
    payrollsError ||
    providersError) as Error | null

  return {
    payrollStats,
    monthlyData,
    financialMetrics,
    payrolls,
    providers,
    dashboardData,
    isLoading,
    error,
  }
}
