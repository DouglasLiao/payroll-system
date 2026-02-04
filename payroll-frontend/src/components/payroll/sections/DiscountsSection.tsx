import React from 'react'
import { Grid, Typography, TextField } from '@mui/material'
import type { Control } from 'react-hook-form'
import type { Provider } from '../../../types'
import { formatCurrency } from '../../../utils/formatters'
import { NumericField } from '../fields/NumericField'

interface PayrollFormInputs {
  provider_id: number
  reference_month: string
  hired_date?: string | null
  overtime_hours_50?: number
  holiday_hours?: number
  night_hours?: number
  late_minutes?: number
  absence_hours?: number
  absence_days?: number
  manual_discounts?: number
  notes?: string
}

interface CalculationsResult {
  lateDiscount: number
  absenceDiscount: number
  workDaysForVT: number
  calculatedVT: number
  totalDiscounts: number
}

interface DiscountsSectionProps {
  control: Control<PayrollFormInputs>
  selectedProvider: Provider | null
  calculations: CalculationsResult
}

export const DiscountsSection: React.FC<DiscountsSectionProps> = ({
  control,
  selectedProvider,
  calculations,
}) => {
  if (!selectedProvider) {
    return (
      <Typography color="text.secondary" sx={{ p: 2 }}>
        Selecione um prestador para visualizar esta seção
      </Typography>
    )
  }

  return (
    <Grid container spacing={1.5}>
      {/* Atrasos */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          Atrasos
        </Typography>
      </Grid>
      <Grid size={{ xs: 6 }}>
        <NumericField
          name="late_minutes"
          label="Minutos de Atraso"
          control={control}
        />
      </Grid>
      <Grid size={{ xs: 6 }}>
        <TextField
          label="Valor do Desconto"
          value={formatCurrency(calculations.lateDiscount)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'error.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'error.dark',
              fontWeight: 600,
            },
          }}
        />
      </Grid>

      {/* Faltas */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          Faltas
        </Typography>
      </Grid>
      <Grid size={{ xs: 6 }}>
        <NumericField
          name="absence_hours"
          label="Horas de Falta"
          control={control}
          helperText="Total de horas faltadas no mês"
        />
      </Grid>
      <Grid size={{ xs: 6 }}>
        <TextField
          label="Desconto por Faltas"
          value={formatCurrency(calculations.absenceDiscount)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'error.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'error.dark',
              fontWeight: 600,
            },
          }}
        />
      </Grid>

      {/* Vale Transporte (quando habilitado) */}
      {selectedProvider.vt_enabled && (
        <>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Vale Transporte (Calculado Automaticamente)
            </Typography>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <NumericField
              name="absence_days"
              label="Dias de Falta"
              control={control}
              helperText="Descontado automaticamente do VT"
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <TextField
              label="Valor Unitário VT/dia"
              value={`R$ ${(selectedProvider.vt_trips_per_day * parseFloat(selectedProvider.vt_fare)).toFixed(2)}`}
              fullWidth
              disabled
              helperText={`${selectedProvider.vt_trips_per_day}× R$ ${selectedProvider.vt_fare} por dia trabalhado`}
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  color: 'info.main',
                  fontWeight: 600,
                },
              }}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <TextField
              label="VT Total Estimado"
              value={formatCurrency(calculations.calculatedVT)}
              fullWidth
              disabled
              helperText={`Ajustado automaticamente (${Math.max(0, calculations.workDaysForVT)} dias trabalhados)`}
              sx={{
                bgcolor: 'info.50',
                '& .MuiInputBase-input.Mui-disabled': {
                  color: 'info.dark',
                  fontWeight: 600,
                },
              }}
            />
          </Grid>
        </>
      )}

      {/* Dias de Falta (quando VT desabilitado) */}
      {!selectedProvider.vt_enabled && (
        <>
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Dias de Falta
            </Typography>
          </Grid>
          <Grid size={{ xs: 12 }}>
            <NumericField
              name="absence_days"
              label="Dias de Falta"
              control={control}
              helperText="Número de dias de falta no mês"
            />
          </Grid>
        </>
      )}

      {/* Descontos Manuais */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          Descontos Manuais
        </Typography>
      </Grid>
      <Grid size={{ xs: 8 }}>
        <NumericField
          name="manual_discounts"
          label="Descontos Manuais (R$)"
          control={control}
          placeholder="0,00"
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Total de Descontos"
          value={formatCurrency(calculations.totalDiscounts)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'error.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'error.dark',
              fontWeight: 700,
              fontSize: '1.1rem',
            },
          }}
        />
      </Grid>
    </Grid>
  )
}
