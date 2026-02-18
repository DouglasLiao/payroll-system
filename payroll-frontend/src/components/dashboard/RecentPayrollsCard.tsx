import { Card, Typography, Box } from '@mui/material'
import { StatusChip } from 'src/components/table'
import { formatCurrency } from 'src/utils/formatters'
import type { Payroll } from 'src/types'

interface RecentPayrollsCardProps {
  payrolls: Payroll[]
  loading?: boolean
  onPayrollClick?: (payroll: Payroll) => void
}

/**
 * Card displaying recent payrolls with clickable cards
 */
export const RecentPayrollsCard = ({
  payrolls,
  loading = false,
  onPayrollClick,
}: RecentPayrollsCardProps) => {
  if (loading) {
    return (
      <Card sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          🧾 Últimas Folhas de Pagamento
        </Typography>
        <Typography color="text.secondary">Carregando...</Typography>
      </Card>
    )
  }

  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        🧾 Últimas Folhas de Pagamento
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {payrolls && payrolls.length > 0 ? (
          payrolls.slice(0, 5).map((payroll) => (
            <Card
              key={payroll.id}
              variant="outlined"
              sx={{
                p: 2,
                minWidth: 200,
                flex: '1 1 calc(20% - 16px)',
                cursor: onPayrollClick ? 'pointer' : 'default',
                transition: 'all 0.2s ease-in-out',
                '&:hover': onPayrollClick
                  ? {
                      boxShadow: 2,
                      borderColor: 'primary.main',
                      transform: 'translateY(-2px)',
                    }
                  : {},
              }}
              onClick={() => onPayrollClick?.(payroll)}
            >
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  mb: 1,
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  {payroll.reference_month}
                </Typography>
                <StatusChip
                  status={payroll.status as 'DRAFT' | 'CLOSED' | 'PAID'}
                />
              </Box>
              <Typography variant="subtitle2" noWrap>
                {payroll.provider_name}
              </Typography>
              <Typography variant="h6" color="primary.main" sx={{ mt: 1 }}>
                {formatCurrency(payroll.net_value)}
              </Typography>
            </Card>
          ))
        ) : (
          <Typography
            color="text.secondary"
            sx={{ textAlign: 'center', width: '100%', py: 3 }}
          >
            Nenhuma folha cadastrada ainda
          </Typography>
        )}
      </Box>
    </Card>
  )
}
