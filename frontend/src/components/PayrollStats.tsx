import { Grid } from '@mui/material'
import { StatCard } from './StatCard'
import type { Payroll } from '../types'

interface PayrollStatsProps {
  payrolls?: Payroll[]
  isLoading: boolean
}

export const PayrollStats = ({ payrolls, isLoading }: PayrollStatsProps) => {
  return (
    <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid size={{ xs: 12, md: 4 }}>
        <StatCard
          title="Total de Folhas"
          value={payrolls?.length || 0}
          loading={isLoading}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <StatCard
          title="Rascunhos"
          value={
            payrolls?.filter((p: Payroll) => p.status === 'DRAFT').length || 0
          }
          loading={isLoading}
        />
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <StatCard
          title="Pagas"
          value={
            payrolls?.filter((p: Payroll) => p.status === 'PAID').length || 0
          }
          color="success.main"
          loading={isLoading}
        />
      </Grid>
    </Grid>
  )
}
