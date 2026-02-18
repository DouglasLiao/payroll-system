import React from 'react'
import { Grid, Typography, TextField, Autocomplete, Alert } from '@mui/material'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import type { Dayjs } from 'dayjs'
import { Controller, type Control, type FieldErrors } from 'react-hook-form'
import type { Provider } from 'src/types'
import { formatCurrency } from 'src/utils/formatters'

export interface PayrollFormInputs {
  name?: string
  provider_id: number
  reference_month: string
  hired_date?: string | null
  overtime_hours_50?: number
  holiday_hours?: number
  night_hours?: number
  late_minutes?: number
  absence_days?: number
  manual_discounts?: number
  notes?: string
}

interface ProportionalInfo {
  workedDays: number
  totalDays: number
  proportionalValue: number
}

interface ContractDataSectionProps {
  control: Control<PayrollFormInputs>
  errors: FieldErrors<PayrollFormInputs>
  providers: Provider[]
  selectedProvider: Provider | null
  selectedMonth: Dayjs | null
  selectedDate: Dayjs | null
  proportionalInfo: ProportionalInfo | null
  hourlyRate: number
  onProviderChange: (providerId: number) => void
  onMonthChange: (month: Dayjs | null) => void
  onDateChange: (date: Dayjs | null) => void
  isEditMode?: boolean
}

export const ContractDataSection: React.FC<ContractDataSectionProps> = ({
  control,
  errors,
  providers,
  selectedProvider,
  selectedMonth,
  selectedDate,
  proportionalInfo,
  hourlyRate,
  onProviderChange,
  onMonthChange,
  onDateChange,
  isEditMode = false,
}) => {
  return (
    <Grid container spacing={1.5}>
      <Grid size={{ xs: 12 }}>
        <Controller
          name="provider_id"
          control={control}
          render={({ field }) => (
            <Autocomplete
              options={providers || []}
              getOptionLabel={(option) => `${option.name} - ${option.role}`}
              value={
                providers?.find((p) => p.id === field.value) ||
                null ||
                undefined
              }
              onChange={(event, newValue) => {
                onProviderChange(newValue?.id || 0)
                field.onChange(newValue?.id || 0)
              }}
              disableClearable
              disabled={isEditMode}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Prestador"
                  error={!!errors.provider_id}
                  helperText={
                    errors.provider_id?.message ||
                    'Selecione o colaborador para a folha de pagamento'
                  }
                  required
                />
              )}
              noOptionsText="Nenhum colaborador encontrado"
              loadingText="Carregando..."
            />
          )}
        />
      </Grid>

      <Grid size={{ xs: 6 }}>
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="pt-br">
          <Controller
            name="reference_month"
            control={control}
            render={({ field }) => (
              <DatePicker
                label="Mês de Referência"
                views={['month', 'year']}
                format="MM/YYYY"
                value={selectedMonth}
                onChange={(newValue) => {
                  onMonthChange(newValue)
                  field.onChange(newValue ? newValue.format('MM/YYYY') : '')
                }}
                disabled={isEditMode}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    error: !!errors.reference_month,
                    helperText:
                      errors.reference_month?.message ||
                      'Selecione o mês da folha de pagamento',
                    required: true,
                  },
                }}
              />
            )}
          />
        </LocalizationProvider>
      </Grid>

      <Grid size={{ xs: 6 }}>
        <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="pt-br">
          <Controller
            name="hired_date"
            control={control}
            render={({ field }) => (
              <DatePicker
                label="Data de Admissão/Início (Opcional)"
                format="DD/MM/YYYY"
                value={selectedDate}
                onChange={(newValue) => {
                  onDateChange(newValue)
                  field.onChange(
                    newValue ? newValue.format('YYYY-MM-DD') : null
                  )
                }}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    helperText:
                      'Preencha se o funcionário começou no meio do mês',
                  },
                }}
              />
            )}
          />
        </LocalizationProvider>
      </Grid>

      {proportionalInfo && (
        <Grid size={{ xs: 12 }}>
          <Alert severity="info" sx={{ mt: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              📅 Salário Proporcional Calculado
            </Typography>
            <Typography variant="body2">
              Dias trabalhados: <strong>{proportionalInfo.workedDays}</strong>{' '}
              de <strong>{proportionalInfo.totalDays}</strong> dias
            </Typography>
            <Typography variant="body2">
              Valor proporcional:{' '}
              <strong>
                {formatCurrency(proportionalInfo.proportionalValue)}
              </strong>
            </Typography>
          </Alert>
        </Grid>
      )}

      {selectedProvider && (
        <>
          <Grid size={{ xs: 3 }}>
            <TextField
              label="Valor Mensal do Contrato"
              value={formatCurrency(selectedProvider.monthly_value)}
              fullWidth
              disabled
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  color: 'text.primary',
                },
              }}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <TextField
              label="Carga Horária Mensal"
              value={`${selectedProvider.monthly_hours}h`}
              fullWidth
              disabled
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  color: 'text.primary',
                },
              }}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <TextField
              label="Percentual de Adiantamento"
              value={`${selectedProvider.advance_percentage}%`}
              fullWidth
              disabled
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  color: 'text.primary',
                },
              }}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <TextField
              label="Valor da Hora"
              value={formatCurrency(hourlyRate)}
              fullWidth
              disabled
              sx={{
                '& .MuiInputBase-input.Mui-disabled': {
                  color: 'primary.main',
                  fontWeight: 600,
                },
                bgcolor: 'action.hover',
              }}
            />
          </Grid>
        </>
      )}
    </Grid>
  )
}
