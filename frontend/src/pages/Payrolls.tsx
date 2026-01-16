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
  Container,
} from '@mui/material'
import {
  Add,
  Visibility,
  Info as InfoIcon,
  FileDownload,
} from '@mui/icons-material'
import { GenericTable } from '../components/GenericTable'
import { StatusChip } from '../components/StatusChip'
import { StatCard } from '../components/StatCard'
import {
  PayrollFiltersComponent,
  type PayrollFilters,
} from '../components/PayrollFilters'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useSnackbar } from 'notistack'
import type { Payroll, Provider } from '../types'
import { formatCurrency } from '../utils/formatters'
import {
  getPayrolls,
  getProviders,
  createPayroll,
  getPayrollDetail,
  closePayroll,
  markPayrollAsPaid,
  downloadPayrollExcel,
} from '../services/api'

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

const Payrolls = () => {
  const [openForm, setOpenForm] = useState(false)
  const [openDetail, setOpenDetail] = useState(false)
  const [selectedPayroll, setSelectedPayroll] = useState<number | null>(null)
  const [filters, setFilters] = useState<PayrollFilters>({
    status: 'all',
    reference_month: '',
  })
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(
    null
  )
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()

  const { data: payrolls, isLoading } = useQuery({
    queryKey: ['payrolls', filters],
    queryFn: () => getPayrolls(filters),
  })

  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  const { data: payrollDetail } = useQuery({
    queryKey: ['payroll-detail', selectedPayroll],
    queryFn: () => getPayrollDetail(selectedPayroll!),
    enabled: !!selectedPayroll && openDetail,
  })

  const createMutation = useMutation({
    mutationFn: createPayroll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      setOpenForm(false)
      enqueueSnackbar('Folha criada com sucesso!', { variant: 'success' })
      reset()
      setSelectedProvider(null)
    },
    onError: (error: Error) =>
      enqueueSnackbar(error.message, { variant: 'error' }),
  })

  const closeMutation = useMutation({
    mutationFn: closePayroll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      queryClient.invalidateQueries({ queryKey: ['payroll-detail'] })
      enqueueSnackbar('Folha fechada com sucesso!', { variant: 'success' })
    },
  })

  const markPaidMutation = useMutation({
    mutationFn: markPayrollAsPaid,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      queryClient.invalidateQueries({ queryKey: ['payroll-detail'] })
      enqueueSnackbar('Folha marcada como paga!', { variant: 'success' })
    },
  })

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

  const onSubmit = (data: PayrollFormInputs) => {
    createMutation.mutate(data)
  }

  const handleViewDetails = (payroll: Payroll) => {
    setSelectedPayroll(payroll.id)
    setOpenDetail(true)
  }

  const handleDownloadExcel = async (payrollId: number) => {
    try {
      await downloadPayrollExcel(payrollId)
      enqueueSnackbar('Excel baixado com sucesso!', { variant: 'success' })
    } catch {
      enqueueSnackbar('Erro ao baixar Excel', { variant: 'error' })
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Folhas de Pagamento</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenForm(true)}
        >
          Nova Folha
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 4 }}>
          <StatCard
            title="Total de Folhas"
            value={payrolls?.length || 0}
            loading={isLoading}
          />
        </Grid>
        <Grid size={{ xs: 4 }}>
          <StatCard
            title="Rascunhos"
            value={
              payrolls?.filter((p: Payroll) => p.status === 'DRAFT').length || 0
            }
            loading={isLoading}
          />
        </Grid>
        <Grid size={{ xs: 4 }}>
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

      {/* Filters */}
      <PayrollFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        providers={providers}
      />

      {/* Table */}
      <GenericTable<Payroll>
        data={payrolls}
        loading={isLoading}
        keyExtractor={(p) => p.id}
        columns={[
          { id: 'provider', label: 'Prestador', accessor: 'provider_name' },
          { id: 'month', label: 'Mês', accessor: 'reference_month' },
          {
            id: 'status',
            label: 'Status',
            render: (p) => (
              <StatusChip
                status={p.status as 'DRAFT' | 'CLOSED' | 'PAID'}
                label={p.status_display}
              />
            ),
          },
          {
            id: 'base',
            label: 'Base',
            align: 'right',
            render: (p) => formatCurrency(p.base_value),
          },
          {
            id: 'earnings',
            label: 'Proventos',
            align: 'right',
            render: (p) => (
              <Box sx={{ color: 'success.main' }}>
                +{formatCurrency(p.total_earnings)}
              </Box>
            ),
          },
          {
            id: 'discounts',
            label: 'Descontos',
            align: 'right',
            render: (p) => (
              <Box sx={{ color: 'error.main' }}>
                -{formatCurrency(p.total_discounts)}
              </Box>
            ),
          },
          {
            id: 'net',
            label: 'Líquido',
            align: 'right',
            render: (p) => (
              <Typography fontWeight={700}>
                {formatCurrency(p.net_value)}
              </Typography>
            ),
          },
          {
            id: 'actions',
            label: 'Ações',
            align: 'right',
            render: (p) => (
              <Button
                size="small"
                startIcon={<Visibility />}
                onClick={() => handleViewDetails(p)}
              >
                Ver
              </Button>
            ),
          },
        ]}
      />

      {/* Form Dialog - REFATORADO EM 4 CARDS */}
      <Dialog
        open={openForm}
        onClose={() => setOpenForm(false)}
        maxWidth="lg"
        fullWidth
      >
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
        <form onSubmit={handleSubmit(onSubmit)}>
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
                      sx={{ fontWeight: 600 }}
                    >
                      ⭐ Resumo do Pagamento
                    </Typography>
                    <Divider sx={{ mb: 2, borderColor: 'primary.light' }} />

                    <Grid container spacing={2}>
                      <Grid size={{ xs: 3 }}>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          Valor do Contrato
                        </Typography>
                        <Typography variant="h6">
                          {selectedProvider
                            ? formatCurrency(selectedProvider.monthly_value)
                            : '-'}
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 3 }}>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          Adiantamento
                        </Typography>
                        <Typography variant="h6">
                          - {formatCurrency(advanceValue)}
                        </Typography>
                      </Grid>
                      <Grid size={{ xs: 3 }}>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          Total Adicionais
                        </Typography>
                        <Typography
                          variant="h6"
                          sx={{ color: 'success.light' }}
                        >
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
                          <Typography variant="h5" sx={{ fontWeight: 700 }}>
                            Valor Final a Pagar:
                          </Typography>
                          <Typography variant="h3" sx={{ fontWeight: 700 }}>
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
          <Box
            sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}
          >
            <Button onClick={() => setOpenForm(false)}>Cancelar</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending || !selectedProvider}
            >
              {createMutation.isPending ? 'Calculando...' : 'Criar Folha'}
            </Button>
          </Box>
        </form>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog
        open={openDetail}
        onClose={() => setOpenDetail(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {payrollDetail?.provider.name} - {payrollDetail?.reference_month}
        </DialogTitle>
        <DialogContent>
          {payrollDetail && (
            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <StatusChip
                    status={payrollDetail.status as 'DRAFT' | 'CLOSED' | 'PAID'}
                    label={payrollDetail.status_display}
                  />
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      color="primary"
                      startIcon={<FileDownload />}
                      onClick={() => handleDownloadExcel(payrollDetail.id)}
                    >
                      Download Excel
                    </Button>
                    {payrollDetail.status === 'DRAFT' && (
                      <Button
                        variant="outlined"
                        onClick={() => closeMutation.mutate(payrollDetail.id)}
                        disabled={closeMutation.isPending}
                      >
                        Fechar Folha
                      </Button>
                    )}
                    {payrollDetail.status === 'CLOSED' && (
                      <Button
                        variant="contained"
                        onClick={() =>
                          markPaidMutation.mutate(payrollDetail.id)
                        }
                        disabled={markPaidMutation.isPending}
                      >
                        Marcar como Paga
                      </Button>
                    )}
                  </Box>
                </Box>
              </Grid>

              <Grid size={{ xs: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="success.main">
                      💰 Proventos
                    </Typography>
                    <Box
                      sx={{
                        '& > div': {
                          display: 'flex',
                          justifyContent: 'space-between',
                          mb: 1,
                        },
                      }}
                    >
                      <div>
                        <Typography variant="body2">Saldo base:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.remaining_value)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">Horas extras:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.overtime_amount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">Feriados:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.holiday_amount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">DSR:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.dsr_amount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">
                          Adicional noturno:
                        </Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.night_shift_amount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="subtitle1" fontWeight={700}>
                          Total:
                        </Typography>
                        <Typography fontWeight={700} color="success.main">
                          {formatCurrency(payrollDetail.total_earnings)}
                        </Typography>
                      </div>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid size={{ xs: 6 }}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="error.main">
                      📉 Descontos
                    </Typography>
                    <Box
                      sx={{
                        '& > div': {
                          display: 'flex',
                          justifyContent: 'space-between',
                          mb: 1,
                        },
                      }}
                    >
                      <div>
                        <Typography variant="body2">Adiantamento:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.advance_value)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">Atrasos:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.late_discount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">Faltas:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.absence_discount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">DSR s/ faltas:</Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.dsr_on_absences)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="body2">
                          Vale transporte:
                        </Typography>
                        <Typography>
                          {formatCurrency(payrollDetail.vt_discount)}
                        </Typography>
                      </div>
                      <div>
                        <Typography variant="subtitle1" fontWeight={700}>
                          Total:
                        </Typography>
                        <Typography fontWeight={700} color="error.main">
                          {formatCurrency(payrollDetail.total_discounts)}
                        </Typography>
                      </div>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid size={{ xs: 12 }}>
                <Card
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'primary.contrastText',
                  }}
                >
                  <CardContent>
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <Typography variant="h5">Valor Líquido</Typography>
                      <Typography variant="h3" fontWeight={700}>
                        {formatCurrency(payrollDetail.net_value)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
      </Dialog>
    </Container>
  )
}

export default Payrolls
