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
  overtimeValue: number
  holidayValue: number
  nightValue: number
  totalOvertime: number
  totalHoliday: number
  totalNight: number
  dsrValue: number
}

interface CalendarInfo {
  workDays: number
  restDays: number
}

interface AdditionalsSectionProps {
  control: Control<PayrollFormInputs>
  selectedProvider: Provider | null
  calculations: CalculationsResult
  calendarInfo: CalendarInfo
}

export const AdditionalsSection: React.FC<AdditionalsSectionProps> = ({
  control,
  selectedProvider,
  calculations,
  calendarInfo,
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
      {/* Hora Extra */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Hora Extra (50%)
        </Typography>
      </Grid>
      <Grid size={{ xs: 4 }}>
        <NumericField
          name="overtime_hours_50"
          label="Horas Extras"
          control={control}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Valor Hora Extra"
          value={formatCurrency(calculations.overtimeValue)}
          fullWidth
          disabled
          sx={{ bgcolor: 'action.hover' }}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Total Hora Extra"
          value={formatCurrency(calculations.totalOvertime)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'success.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'success.dark',
              fontWeight: 600,
            },
          }}
        />
      </Grid>

      {/* Feriados */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ mt: 1, mb: 1, fontWeight: 600 }}>
          Feriados Trabalhados
        </Typography>
      </Grid>
      <Grid size={{ xs: 4 }}>
        <NumericField
          name="holiday_hours"
          label="Horas em Feriado"
          control={control}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Valor Hora Feriado"
          value={formatCurrency(calculations.holidayValue)}
          fullWidth
          disabled
          sx={{ bgcolor: 'action.hover' }}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Total Feriado"
          value={formatCurrency(calculations.totalHoliday)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'success.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'success.dark',
              fontWeight: 600,
            },
          }}
        />
      </Grid>

      {/* DSR */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ mt: 1, mb: 1, fontWeight: 600 }}>
          DSR Contratual
        </Typography>
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Fórmula DSR"
          value={`(HE+Fer)/${calendarInfo.workDays}×${calendarInfo.restDays}`}
          fullWidth
          disabled
          sx={{ bgcolor: 'action.hover' }}
        />
      </Grid>
      <Grid size={{ xs: 8 }}>
        <TextField
          label="Valor DSR (horas extras + feriados)"
          value={formatCurrency(calculations.dsrValue)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'success.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'success.dark',
              fontWeight: 600,
            },
          }}
        />
      </Grid>

      {/* Horas Noturnas */}
      <Grid size={{ xs: 12 }}>
        <Typography variant="subtitle2" sx={{ mt: 1, mb: 1, fontWeight: 600 }}>
          Horas Noturnas (20% adicional)
        </Typography>
      </Grid>
      <Grid size={{ xs: 4 }}>
        <NumericField
          name="night_hours"
          label="Horas Noturnas"
          control={control}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Valor Hora Noturna"
          value={formatCurrency(calculations.nightValue)}
          fullWidth
          disabled
          sx={{ bgcolor: 'action.hover' }}
        />
      </Grid>
      <Grid size={{ xs: 4 }}>
        <TextField
          label="Total Noturno"
          value={formatCurrency(calculations.totalNight)}
          fullWidth
          disabled
          sx={{
            bgcolor: 'success.100',
            '& .MuiInputBase-input.Mui-disabled': {
              color: 'success.dark',
              fontWeight: 600,
            },
          }}
        />
      </Grid>
    </Grid>
  )
}
