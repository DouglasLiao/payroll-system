import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  Tooltip,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { Provider, Payroll, PayrollDetail } from 'src/types'
import { getMonthCalendarInfo } from 'src/utils/calendarUtils'
import { usePayrollCalculations } from 'src/components/payroll/hooks/usePayrollCalculations'
import { ContractDataSection } from 'src/components/payroll/sections/ContractDataSection'
import { AdditionalsSection } from 'src/components/payroll/sections/AdditionalsSection'
import { DiscountsSection } from 'src/components/payroll/sections/DiscountsSection'
import { PaymentSummarySection } from 'src/components/payroll/sections/PaymentSummarySection'

dayjs.extend(customParseFormat)
// Schema de validação
const payrollSchema = z.object({
  provider_id: z.number().min(1, 'Selecione um prestador'),
  reference_month: z
    .string()
    .regex(/^\d{2}\/\d{4}$/, 'Formato deve ser MM/YYYY'),
  hired_date: z.string().nullable().optional(),
  overtime_hours_50: z.number().min(0).optional(),
  holiday_hours: z.number().min(0).optional(),
  night_hours: z.number().min(0).optional(),
  late_minutes: z.number().min(0).optional(),
  absence_days: z.number().min(0).optional(),
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
  editingPayroll?: Payroll | PayrollDetail | null
}

interface ProportionalInfo {
  workedDays: number
  totalDays: number
  proportionalValue: number
}

export const PayrollFormDialog = ({
  open,
  onClose,
  onSubmit,
  providers,
  isPending,
  editingPayroll,
}: PayrollFormDialogProps) => {
  const isEditMode = !!editingPayroll
  const [selectedProvider, setSelectedProvider] = useState<Provider | null>(
    null
  )
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(null)
  const [selectedMonth, setSelectedMonth] = useState<Dayjs | null>(null)
  const [proportionalInfo, setProportionalInfo] =
    useState<ProportionalInfo | null>(null)
  const [expanded, setExpanded] = useState<string[]>(['contract'])

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
      hired_date: null,
      overtime_hours_50: 0,
      holiday_hours: 0,
      night_hours: 0,
      late_minutes: 0,
      absence_days: 0,
      manual_discounts: 0,
      notes: '',
    },
  })

  // eslint-disable-next-line react-hooks/incompatible-library
  const watchedValues = watch()

  // Reset form when editingPayroll changes
  useEffect(() => {
    if (editingPayroll) {
      reset({
        provider_id: editingPayroll.provider.id,
        reference_month: editingPayroll.reference_month,
        hired_date: editingPayroll.hired_date || null,
        overtime_hours_50: Number(editingPayroll.overtime_hours_50) || 0,
        holiday_hours: Number(editingPayroll.holiday_hours) || 0,
        night_hours: Number(editingPayroll.night_hours) || 0,
        late_minutes: editingPayroll.late_minutes || 0,
        absence_days: editingPayroll.absence_days || 0,
        manual_discounts: Number(editingPayroll.manual_discounts) || 0,
        notes: editingPayroll.notes || '',
      })

      // Set local state values
      setSelectedMonth(dayjs(editingPayroll.reference_month, 'MM/YYYY'))

      if (editingPayroll.hired_date) {
        setSelectedDate(dayjs(editingPayroll.hired_date))
      } else {
        setSelectedDate(null)
      }
    } else {
      reset({
        provider_id: 0,
        reference_month: '',
        hired_date: null,
        overtime_hours_50: 0,
        holiday_hours: 0,
        night_hours: 0,
        late_minutes: 0,
        absence_days: 0,
        manual_discounts: 0,
        notes: '',
      })
      setSelectedMonth(null)
      setSelectedDate(null)
      setSelectedProvider(null)
    }
  }, [editingPayroll, reset])

  // Calendar info for DSR calculations
  const calendarInfo = watchedValues.reference_month
    ? getMonthCalendarInfo(watchedValues.reference_month)
    : { workDays: 25, restDays: 6 }

  // Use the calculation hook
  const calculations = usePayrollCalculations(
    selectedProvider,
    watchedValues,
    calendarInfo
  )

  // Update selected provider when provider_id changes
  useEffect(() => {
    if (watchedValues.provider_id && providers) {
      const provider = providers.find(
        (p: Provider) => p.id === watchedValues.provider_id
      )
      setSelectedProvider(provider || null)
    }
  }, [watchedValues.provider_id, providers])

  // Auto-expand all sections when provider is selected
  useEffect(() => {
    if (selectedProvider) {
      setExpanded(['contract', 'additionals', 'discounts', 'summary'])
    }
  }, [selectedProvider])

  // Calculate proportional salary when hired_date changes
  useEffect(() => {
    if (selectedDate && selectedProvider && watchedValues.reference_month) {
      const [month, year] = watchedValues.reference_month.split('/')
      const refMonth = parseInt(month)
      const refYear = parseInt(year)

      if (
        selectedDate.month() + 1 === refMonth &&
        selectedDate.year() === refYear
      ) {
        const totalDays = selectedDate.daysInMonth()
        const workedDays = totalDays - selectedDate.date() + 1
        const monthlyValue = Number(selectedProvider.monthly_value)
        const proportionalValue = (monthlyValue * workedDays) / totalDays

        setProportionalInfo({
          workedDays,
          totalDays,
          proportionalValue,
        })
      } else {
        setProportionalInfo(null)
      }
    } else {
      setProportionalInfo(null)
    }
  }, [selectedDate, selectedProvider, watchedValues.reference_month])

  const handleAccordionChange =
    (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded((prev) =>
        isExpanded ? [...prev, panel] : prev.filter((p) => p !== panel)
      )
    }

  const handleFormClose = () => {
    reset()
    setSelectedProvider(null)
    setSelectedDate(null)
    setSelectedMonth(null)
    setProportionalInfo(null)
    setExpanded(['contract'])
    onClose()
  }

  const handleFormSubmit = (data: PayrollFormInputs) => {
    onSubmit(data)
    reset()
    setSelectedProvider(null)
    setSelectedDate(null)
    setSelectedMonth(null)
    setProportionalInfo(null)
    setExpanded(['contract'])
  }

  const handleProviderChange = (providerId: number) => {
    const provider = providers?.find((p) => p.id === providerId)
    setSelectedProvider(provider || null)
  }

  const handleMonthChange = (month: Dayjs | null) => {
    setSelectedMonth(month)
  }

  const handleDateChange = (date: Dayjs | null) => {
    setSelectedDate(date)
  }

  return (
    <Dialog open={open} onClose={handleFormClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isEditMode ? 'Editar Folha de Pagamento' : 'Nova Folha de Pagamento'}
          <Tooltip title="Hora extra e DSR são adicionais contratuais (PJ), não obrigações legais">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </DialogTitle>
      <form onSubmit={handleSubmit(handleFormSubmit)}>
        <DialogContent>
          {/* Accordion 1: Dados do Contrato */}
          <Accordion
            expanded={expanded.includes('contract')}
            onChange={handleAccordionChange('contract')}
            sx={{
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: '8px',
              overflow: 'hidden',
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                bgcolor: 'background.paper',
                '&.Mui-expanded': {
                  minHeight: 40,
                },
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Dados do Contrato
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <ContractDataSection
                control={control}
                errors={errors}
                providers={providers || []}
                selectedProvider={selectedProvider}
                selectedMonth={selectedMonth}
                selectedDate={selectedDate}
                proportionalInfo={proportionalInfo}
                hourlyRate={calculations.hourlyRate}
                onProviderChange={handleProviderChange}
                onMonthChange={handleMonthChange}
                onDateChange={handleDateChange}
                isEditMode={isEditMode}
              />
            </AccordionDetails>
          </Accordion>

          {/* Accordion 2: Adicionais Contratuais */}
          <Accordion
            expanded={expanded.includes('additionals')}
            onChange={handleAccordionChange('additionals')}
            disabled={!selectedProvider}
            sx={{
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: '8px',
              overflow: 'hidden',
              mb: 1,
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                bgcolor: 'success.50',
                '&.Mui-expanded': {
                  minHeight: 48,
                },
              }}
            >
              <Typography
                variant="h6"
                sx={{ color: 'success.main', fontWeight: 600 }}
              >
                Adicionais Contratuais
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ bgcolor: 'success.50' }}>
              <AdditionalsSection
                control={control}
                selectedProvider={selectedProvider}
                calculations={calculations}
                calendarInfo={calendarInfo}
              />
            </AccordionDetails>
          </Accordion>

          {/* Accordion 3: Descontos */}
          <Accordion
            expanded={expanded.includes('discounts')}
            onChange={handleAccordionChange('discounts')}
            disabled={!selectedProvider}
            sx={{
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: '8px',
              overflow: 'hidden',
              mb: 1,
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                bgcolor: 'error.50',
                '&.Mui-expanded': {
                  minHeight: 48,
                },
              }}
            >
              <Typography
                variant="h6"
                sx={{ color: 'error.main', fontWeight: 600 }}
              >
                Descontos
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ bgcolor: 'error.50' }}>
              <DiscountsSection
                control={control}
                selectedProvider={selectedProvider}
                calculations={calculations}
              />
            </AccordionDetails>
          </Accordion>

          {/* Accordion 4: Resumo do Pagamento */}
          <Accordion
            expanded={expanded.includes('summary')}
            onChange={handleAccordionChange('summary')}
            disabled={!selectedProvider}
            sx={{
              '&:before': { display: 'none' },
              boxShadow: 'none',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: '8px',
              overflow: 'hidden',
              mb: 1,
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&.Mui-expanded': {
                  minHeight: 48,
                },
              }}
            >
              <Typography
                variant="h6"
                sx={{ color: 'primary.contrastText', fontWeight: 600 }}
              >
                Resumo do Pagamento
              </Typography>
            </AccordionSummary>
            <AccordionDetails
              sx={{
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
              }}
            >
              <PaymentSummarySection
                selectedProvider={selectedProvider}
                calculations={calculations}
              />
            </AccordionDetails>
          </Accordion>

          {/* Observações */}
          <Box sx={{ mt: 2 }}>
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
          </Box>
        </DialogContent>

        <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Button onClick={handleFormClose}>Cancelar</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isPending || !selectedProvider}
          >
            {isPending
              ? 'Salvando...'
              : isEditMode
                ? 'Salvar Alterações'
                : 'Criar Folha'}
          </Button>
        </Box>
      </form>
    </Dialog>
  )
}
