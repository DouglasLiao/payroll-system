import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Divider,
  Tooltip,
  IconButton,
} from '@mui/material'
import { Info as InfoIcon } from '@mui/icons-material'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { Provider } from '../types'
import { formatCurrency } from '../utils/formatters'

// Schema de validação
const payrollSchema = z.object({
  provider_id: z.number().min(1, 'Selecione um prestador'),
  reference_month: z
    .string()
    .regex(/^\d{2}\/\d{4}$/, 'Formato deve ser MM/YYYY'),
  overtime_hours_50: z.number().min(0).optional(),
  holiday_hours: z.number().min(0).optional(),
  night_hours: z.number().min(0).optional(),
  late_minutes: z.number().min(0).optional(),
  absence_hours: z.number().min(0).optional(),
  manual_discounts: z.number().min(0).optional(),
  notes: z.string().optional(),
})

type PayrollFormInputs = z.infer<typeof payrollSchema>

interface PayrollFormDialogProps {
  open: boolean
  onClose: () => void
  onSubmit: (data: PayrollFormInputs) => void
  providers?: Provider[]
  isPending: boolean
}

export const PayrollFormDialog = ({
  open,
  onClose,
  onSubmit,
  providers,
  isPending,
}: PayrollFormDialogProps) => {
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(
    null
  )

  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<PayrollFormInputs>({
    resolver: zodResolver(payrollSchema),
    defaultValues: {
      provider_id: 0,
      reference_month: '',
      overtime_hours_50: 0,
      holiday_hours: 0,
      night_hours: 0,
      late_minutes: 0,
      absence_hours: 0,
      manual_discounts: 0,
      notes: '',
    },
  })

  const watchedValues = watch()

  // Calculated values baseados no provider selecionado
  const hourlyRate = selectedProvider
    ? Number(selectedProvider.monthly_value) / selectedProvider.monthly_hours
    : 0

  const overtimeValue = hourlyRate * 1.5
  const holidayValue = hourlyRate * 2
  const totalOvertime = (watchedValues.overtime_hours_50 || 0) * overtimeValue
  const totalHoliday = (watchedValues.holiday_hours || 0) * holidayValue
  const dsrPercentage = 16.67
  const dsrValue = totalOvertime * (dsrPercentage / 100)
  const lateDiscount = ((watchedValues.late_minutes || 0) / 60) * hourlyRate
  const totalAdditionals = totalOvertime + totalHoliday + dsrValue
  const totalDiscounts = lateDiscount + (watchedValues.manual_discounts || 0)
  const advanceValue = selectedProvider
    ? Number(selectedProvider.monthly_value) *
      (Number(selectedProvider.advance_percentage) / 100)
    : 0
  const finalValue = selectedProvider
    ? Number(selectedProvider.monthly_value) -
      advanceValue +
      totalAdditionals -
      totalDiscounts
    : 0

  useEffect(() => {
    if (watchedValues.provider_id && providers) {
      const provider = providers.find(
        (p: Provider) => p.id === watchedValues.provider_id
      )
      setSelectedProvider(provider || null)
    }
  }, [watchedValues.provider_id, providers])

  // Helper function to handle numeric field changes
  const handleNumericChange =
    (field: { onChange: (value: number) => void }) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value
      field.onChange(val === '' ? 0 : parseFloat(val) || 0)
    }

  const handleFormClose = () => {
    reset()
    setSelectedProvider(null)
    onClose()
  }

  const handleFormSubmit = (data: PayrollFormInputs) => {
    onSubmit(data)
    reset()
    setSelectedProvider(null)
  }

  return (
    <Dialog open={open} onClose={handleFormClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          Nova Folha de Pagamento
          <Tooltip title="Hora extra e DSR são adicionais contratuais (PJ), não obrigações legais">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogTitle>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogContent>
          <Grid container spacing={3}>
            {/* CARD 1 - DADOS DO CONTRATO */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined">
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ color: 'primary.main', fontWeight: 600 }}
                  >
                    📋 Dados do Contrato
                  </Typography>
                  <Divider sx={{ mb: 2 }} />

                  <Grid container spacing={2}>
                    <Grid size={{ xs: 6 }}>
                      <Controller
                        name="provider_id"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            select
                            label="Prestador"
                            fullWidth
                            error={!!errors.provider_id}
                            helperText={errors.provider_id?.message}
                            onChange={(e) =>
                              field.onChange(parseInt(e.target.value))
                            }
                          >
                            <MenuItem value={0}>Selecione...</MenuItem>
                            {providers?.map((p: Provider) => (
                              <MenuItem key={p.id} value={p.id}>
                                {p.name} - {p.role}
                              </MenuItem>
                            ))}
                          </TextField>
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Controller
                        name="reference_month"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Mês de Referência"
                            placeholder="01/2026"
                            fullWidth
                            error={!!errors.reference_month}
                            helperText={errors.reference_month?.message}
                          />
                        )}
                      />
                    </Grid>

                    {selectedProvider && (
                      <>
                        <Grid size={{ xs: 3 }}>
                          <TextField
                            label="Valor Mensal do Contrato"
                            value={formatCurrency(
                              selectedProvider.monthly_value
                            )}
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
                </CardContent>
              </Card>
            </Grid>

            {/* CARD 2 - ADICIONAIS CONTRATUAIS */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined" sx={{ bgcolor: 'success.50' }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ color: 'success.main', fontWeight: 600 }}
                  >
                    💰 Adicionais Contratuais
                  </Typography>
                  <Divider sx={{ mb: 2 }} />

                  <Grid container spacing={2}>
                    {/* Hora Extra */}
                    <Grid size={{ xs: 12 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{ mb: 1, fontWeight: 600 }}
                      >
                        Hora Extra (50%)
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <Controller
                        name="overtime_hours_50"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Horas Extras"
                            fullWidth
                            value={field.value || ''}
                            onChange={handleNumericChange(field)}
                            placeholder="0"
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <TextField
                        label="Valor Hora Extra"
                        value={formatCurrency(overtimeValue)}
                        fullWidth
                        disabled
                        sx={{ bgcolor: 'action.hover' }}
                      />
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <TextField
                        label="Total Hora Extra"
                        value={formatCurrency(totalOvertime)}
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
                      <Typography
                        variant="subtitle2"
                        sx={{ mt: 1, mb: 1, fontWeight: 600 }}
                      >
                        Feriados Trabalhados
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <Controller
                        name="holiday_hours"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Horas em Feriado"
                            fullWidth
                            value={field.value || ''}
                            onChange={handleNumericChange(field)}
                            placeholder="0"
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <TextField
                        label="Valor Hora Feriado"
                        value={formatCurrency(holidayValue)}
                        fullWidth
                        disabled
                        sx={{ bgcolor: 'action.hover' }}
                      />
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <TextField
                        label="Total Feriado"
                        value={formatCurrency(totalHoliday)}
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
                      <Typography
                        variant="subtitle2"
                        sx={{ mt: 1, mb: 1, fontWeight: 600 }}
                      >
                        DSR Contratual
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <TextField
                        label="Percentual DSR"
                        value={`${dsrPercentage}%`}
                        fullWidth
                        disabled
                        sx={{ bgcolor: 'action.hover' }}
                      />
                    </Grid>
                    <Grid size={{ xs: 8 }}>
                      <TextField
                        label="Valor DSR (base: horas extras)"
                        value={formatCurrency(dsrValue)}
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
                </CardContent>
              </Card>
            </Grid>

            {/* CARD 3 - DESCONTOS */}
            <Grid size={{ xs: 12 }}>
              <Card variant="outlined" sx={{ bgcolor: 'error.50' }}>
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ color: 'error.main', fontWeight: 600 }}
                  >
                    📉 Descontos
                  </Typography>
                  <Divider sx={{ mb: 2 }} />

                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{ mb: 1, fontWeight: 600 }}
                      >
                        Atrasos
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Controller
                        name="late_minutes"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Minutos de Atraso"
                            fullWidth
                            value={field.value || ''}
                            onChange={handleNumericChange(field)}
                            placeholder="0"
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <TextField
                        label="Valor do Desconto"
                        value={formatCurrency(lateDiscount)}
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

                    <Grid size={{ xs: 12 }}>
                      <Typography
                        variant="subtitle2"
                        sx={{ mt: 1, mb: 1, fontWeight: 600 }}
                      >
                        Outros Descontos
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <Controller
                        name="absence_hours"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Horas de Falta"
                            fullWidth
                            value={field.value || ''}
                            onChange={handleNumericChange(field)}
                            placeholder="0"
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <Controller
                        name="manual_discounts"
                        control={control}
                        render={({ field }) => (
                          <TextField
                            {...field}
                            label="Descontos Manuais (R$)"
                            fullWidth
                            value={field.value || ''}
                            onChange={handleNumericChange(field)}
                            placeholder="0,00"
                          />
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 4 }}>
                      <TextField
                        label="Total de Descontos"
                        value={formatCurrency(totalDiscounts)}
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
                </CardContent>
              </Card>
            </Grid>

            {/* CARD 4 - RESUMO DO PAGAMENTO */}
            <Grid size={{ xs: 12 }}>
              <Card
                sx={{
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                }}
              >
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontWeight: 600, color: 'primary.contrastText' }}
                  >
                    ⭐ Resumo do Pagamento
                  </Typography>
                  <Divider sx={{ mb: 2, borderColor: 'primary.light' }} />

                  <Grid container spacing={2}>
                    <Grid size={{ xs: 3 }}>
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Valor do Contrato
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{ color: 'primary.contrastText' }}
                      >
                        {selectedProvider
                          ? formatCurrency(selectedProvider.monthly_value)
                          : '-'}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 3 }}>
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Adiantamento
                      </Typography>
                      <Typography
                        variant="h6"
                        sx={{ color: 'primary.contrastText' }}
                      >
                        - {formatCurrency(advanceValue)}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 3 }}>
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Total Adicionais
                      </Typography>
                      <Typography variant="h6" sx={{ color: 'success.light' }}>
                        + {formatCurrency(totalAdditionals)}
                      </Typography>
                    </Grid>
                    <Grid size={{ xs: 3 }}>
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Total Descontos
                      </Typography>
                      <Typography variant="h6" sx={{ color: 'error.light' }}>
                        - {formatCurrency(totalDiscounts)}
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
                            color: 'primary.contrastText',
                          }}
                        >
                          Valor Final a Pagar:
                        </Typography>
                        <Typography
                          variant="h3"
                          sx={{
                            fontWeight: 700,
                            color: 'primary.contrastText',
                          }}
                        >
                          {formatCurrency(finalValue)}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid size={{ xs: 12 }}>
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Observações"
                    multiline
                    rows={2}
                    fullWidth
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Button onClick={handleFormClose}>Cancelar</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending || !selectedProvider}
          >
            {isPending ? 'Calculando...' : 'Criar Folha'}
          </Button>
        </Box>
      </form>
    </Dialog>
  )
}
