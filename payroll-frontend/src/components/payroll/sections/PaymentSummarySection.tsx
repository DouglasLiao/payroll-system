import React from 'react'
import { Grid, Typography, Box, Divider } from '@mui/material'
import type { Provider } from '../../../types'
import { formatCurrency } from '../../../utils/formatters'

interface CalculationsResult {
  totalAdditionals: number
  totalDiscounts: number
  advanceValue: number
  finalValue: number
}

interface PaymentSummarySectionProps {
  selectedProvider: Provider | null
  calculations: CalculationsResult
}

export const PaymentSummarySection: React.FC<PaymentSummarySectionProps> = ({
  selectedProvider,
  calculations,
}) => {
  if (!selectedProvider) {
    return (
      <Typography color="text.secondary" sx={{ p: 2 }}>
        Selecione um prestador para visualizar o resumo
      </Typography>
    )
  }

  return (
    <Grid container spacing={1.5}>
      <Grid size={{ xs: 3 }}>
        <Typography variant="caption" sx={{ opacity: 0.8, color: 'inherit' }}>
          Valor do Contrato
        </Typography>
        <Typography variant="h6" sx={{ color: 'inherit' }}>
          {formatCurrency(selectedProvider.monthly_value)}
        </Typography>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Typography variant="caption" sx={{ opacity: 0.8, color: 'inherit' }}>
          Adiantamento
        </Typography>
        <Typography variant="h6" sx={{ color: 'inherit' }}>
          - {formatCurrency(calculations.advanceValue)}
        </Typography>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Typography variant="caption" sx={{ opacity: 0.8, color: 'inherit' }}>
          Total Adicionais
        </Typography>
        <Typography variant="h6" sx={{ color: 'success.light' }}>
          + {formatCurrency(calculations.totalAdditionals)}
        </Typography>
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Typography variant="caption" sx={{ opacity: 0.8, color: 'inherit' }}>
          Total Descontos
        </Typography>
        <Typography variant="h6" sx={{ color: 'error.light' }}>
          - {formatCurrency(calculations.totalDiscounts)}
        </Typography>
      </Grid>
      <Grid size={{ xs: 12 }}>
        <Divider sx={{ my: 1, borderColor: 'primary.light' }} />
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography
            variant="h5"
            sx={{
              fontWeight: 700,
              color: 'inherit',
            }}
          >
            Valor Final a Pagar:
          </Typography>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              color: 'inherit',
            }}
          >
            {formatCurrency(calculations.finalValue)}
          </Typography>
        </Box>
      </Grid>
    </Grid>
  )
}
