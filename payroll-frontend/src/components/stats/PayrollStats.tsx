import { Grid } from '@mui/material'
import { StatCard } from 'src/components/stats/StatCard'
import { useQuery } from '@tanstack/react-query'
import { getPayrollStats } from 'src/services/payrollApi'

export const PayrollStats = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['payroll-stats'],
    queryFn: getPayrollStats,
  })

  return (
    <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid size={{ xs: 12, md: 4 }}>
        <StatCard
          title="Total de Folhas"
          value={data?.total || 0}
          loading={isLoading}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <StatCard
          title="Rascunhos"
          value={data?.draft || 0}
          loading={isLoading}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <StatCard
          title="Pagas"
          value={data?.paid || 0}
          color="success.main"
          loading={isLoading}
        />
      </Grid>
    </Grid>
  )
}
