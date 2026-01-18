import { Card, Typography, Box } from '@mui/material'
import { StatusChip } from '../StatusChip'
import { formatCurrency } from '../../utils/formatters'
import type { Payment } from '../../types'

interface RecentActivityCardProps {
  activities: Payment[]
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
        activities.map((payment) => (
          <Box
            key={payment.id}
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
                {payment.provider_name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {payment.reference}
              </Typography>
            </Box>
            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="subtitle2" fontWeight="bold">
                {formatCurrency(payment.total_calculated)}
              </Typography>
              <StatusChip status={payment.status} />
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
