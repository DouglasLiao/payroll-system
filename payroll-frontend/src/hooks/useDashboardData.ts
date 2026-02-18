import { useQuery } from '@tanstack/react-query'
import { getDashboardStats, type DashboardFilters } from 'src/services/api'

/**
 * Custom hook to fetch dashboard data from backend
 * Supports filtering by period (7d, 30d, 90d, 1y, all)
 * All calculations are done server-side for optimal performance
 */
export const useDashboardData = (filters?: DashboardFilters) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard', filters],
    queryFn: () => getDashboardStats(filters),
    staleTime: 30000, // Cache for 30 seconds
  })

  return {
    stats: data?.stats,
    monthlyData: data?.monthly_aggregation || {},
    trends: data?.trends,
    recentActivity: data?.recent_activity || [],
    isLoading,
    error,
  }
}
