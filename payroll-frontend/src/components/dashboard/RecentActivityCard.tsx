import { Card, Typography, Box } from '@mui/material'
import { StatusChip } from 'src/components/table'
import { formatCurrency } from 'src/utils/formatters'
import type { Payroll } from 'src/types'

interface RecentActivityCardProps {
  activities: Payroll[]
  loading?: boolean
}

/**
 * Card displaying recent payment activities
 */
export const RecentActivityCard = ({
  activities,
  loading = false,
}: RecentActivityCardProps) => {
  if (loading) {
    return (
      <Card sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>
          🕐 Atividade Recente
        </Typography>
        <Typography color="text.secondary">Carregando...</Typography>
      </Card>
    )
  }

  return (
    <Card sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        🕐 Atividade Recente
      </Typography>

      {activities && activities.length > 0 ? (
        activities.map((payroll) => (
          <Box
            key={payroll.id}
            sx={{
              mb: 2,
              pb: 2,
              borderBottom: '1px solid',
              borderColor: 'divider',
              display: 'flex',
              justifyContent: 'space-between',
              '&:last-child': {
                borderBottom: 'none',
                mb: 0,
                pb: 0,
              },
            }}
          >
            <Box>
              <Typography variant="subtitle2">
                {payroll.provider_name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {payroll.reference_month}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="subtitle2" fontWeight="bold">
                {formatCurrency(payroll.net_value)}
              </Typography>
              <StatusChip
                status={payroll.status as 'DRAFT' | 'CLOSED' | 'PAID'}
              />
            </Box>
          </Box>
        ))
      ) : (
        <Typography color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
          Nenhuma atividade recente
        </Typography>
      )}
    </Card>
  )
}
