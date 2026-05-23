import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid,
  TextField,
  Typography,
} from '@mui/material'
import { CheckCircle, Error as ErrorIcon } from '@mui/icons-material'
import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useEffect } from 'react'
import { CustomMenuItem } from 'src/components/menu/CustomMenuItem'
import { CPFInput } from 'src/components/inputs/InputMasks'
import {
  validateCPF,
  validateCNPJ,
  onlyLetters,
  validateEmail,
  isPositiveNumber,
} from 'src/utils/validators'
import type { Provider } from 'src/types'

// ── Schema ────────────────────────────────────────────────────────────────────

const providerSchema = z
  .object({
    name: z.string().optional().or(z.literal('')),

    document: z
      .string()
      .min(1, 'CPF ou CNPJ é obrigatório')
      .refine((val) => {
        const cleaned = val.replace(/\D/g, '')
        return cleaned.length === 11 || cleaned.length === 14
      }, 'CPF deve ter 11 dígitos ou CNPJ 14 dígitos')
      .refine((val) => {
        const cleaned = val.replace(/\D/g, '')
        if (cleaned.length === 11) return validateCPF(val)
        if (cleaned.length === 14) return validateCNPJ(val)
        return false
      }, 'CPF ou CNPJ inválido'),

    role: z.string().min(2, 'Cargo é obrigatório').max(50, 'Cargo muito longo'),

    monthly_value: z
      .string()
      .min(1, 'Valor mensal é obrigatório')
      .refine((val) => isPositiveNumber(val), 'Valor deve ser maior que zero'),

    payment_method: z.enum(['PIX', 'TED', 'TRANSFER'], {
      message: 'Selecione um método de pagamento válido',
    }),

    email: z
      .string()
      .min(1, 'O E-mail é obrigatório para enviar o convite')
      .refine((val) => validateEmail(val), 'Email inválido'),

    description: z.string().max(500, 'Descrição muito longa').optional(),

    vt_enabled: z.boolean().optional(),
    vt_fare: z.string().optional(),
    vt_trips_per_day: z.number().min(0).optional(),
  })

export type ProviderFormInputs = z.infer<typeof providerSchema>

const DEFAULT_PROVIDER_VALUES: ProviderFormInputs = {
  name: '',
  document: '',
  role: '',
  monthly_value: '',
  payment_method: 'PIX',
  email: '',
  description: '',
  vt_enabled: false,
  vt_fare: '4.60',
  vt_trips_per_day: 4,
}

// ── Props ─────────────────────────────────────────────────────────────────────

interface ProviderDialogProps {
  open: boolean
  provider?: Provider | null
  onClose: () => void
  onSubmit: (data: ProviderFormInputs) => void
  isSubmitting?: boolean
}

// ── Component ─────────────────────────────────────────────────────────────────

export const ProviderDialog = ({
  open,
  provider,
  onClose,
  onSubmit,
  isSubmitting = false,
}: ProviderDialogProps) => {
  const {
    control,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<ProviderFormInputs>({
    resolver: zodResolver(providerSchema),
    defaultValues: DEFAULT_PROVIDER_VALUES,
  })

  const paymentMethod = watch('payment_method')
  const vtEnabled = watch('vt_enabled')

  // Populate form when editing
  useEffect(() => {
    if (provider) {
      reset({
        name: provider.name || '',
        document: (provider as any).document || '', // Added document field
        role: provider.role,
        monthly_value: provider.monthly_value,
        payment_method: provider.payment_method,
        email: provider.email || '',
        description: provider.description || '',
        vt_enabled: provider.vt_enabled || false,
        vt_fare: provider.vt_fare || '4.60',
        vt_trips_per_day: provider.vt_trips_per_day || 4,
      })
    } else {
      reset(DEFAULT_PROVIDER_VALUES)
    }
  }, [provider, reset, open])

  const handleClose = () => {
    reset(DEFAULT_PROVIDER_VALUES)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {provider ? 'Editar Colaborador' : 'Novo Colaborador'}
      </DialogTitle>

      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            {/* Nome */}
            <Grid size={{ xs: 12 }}>
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Nome"
                    fullWidth
                    error={!!errors.name}
                    helperText={errors.name?.message}
                  />
                )}
              />
            </Grid>

            {/* CPF/CNPJ */}
            <Grid size={{ xs: 12 }}>
              <Controller
                name="document"
                control={control}
                render={({ field, fieldState }) => (
                  <CPFInput
                    {...field}
                    label="CPF/CNPJ"
                    fullWidth
                    required
                    disabled={!!provider && !!(provider as any).document}
                    error={!!fieldState.error}
                    helperText={
                      provider && (provider as any).document
                        ? 'CPF/CNPJ não pode ser alterado'
                        : fieldState.error?.message
                    }
                    InputProps={{
                      endAdornment: fieldState.error ? (
                        <ErrorIcon color="error" fontSize="small" />
                      ) : field.value && !fieldState.error ? (
                        <CheckCircle color="success" fontSize="small" />
                      ) : null,
                    }}
                  />
                )}
              />
            </Grid>

            {/* Cargo + Valor Mensal */}
            <Grid size={{ xs: 6 }}>
              <Controller
                name="role"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Cargo"
                    fullWidth
                    error={!!errors.role}
                    helperText={errors.role?.message}
                  />
                )}
              />
            </Grid>
            <Grid size={{ xs: 6 }}>
              <Controller
                name="monthly_value"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Valor Mensal (R$)"
                    fullWidth
                    error={!!errors.monthly_value}
                    helperText={errors.monthly_value?.message}
                  />
                )}
              />
            </Grid>

            {/* Forma de Pagamento */}
            <Grid size={{ xs: 12 }}>
              <Controller
                name="payment_method"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    label="Forma de Pagamento"
                    fullWidth
                  >
                    <CustomMenuItem value="PIX">PIX</CustomMenuItem>
                    <CustomMenuItem value="TED">TED</CustomMenuItem>
                    <CustomMenuItem value="TRANSFER">
                      Transferência Bancária
                    </CustomMenuItem>
                  </TextField>
                )}
              />
            </Grid>

            {/* Email */}
            <Grid size={{ xs: 12 }}>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Email (Obrigatório para Convite)"
                    fullWidth
                    required
                    error={!!errors.email}
                    helperText={errors.email?.message || 'O prestador receberá o convite neste e-mail'}
                  />
                )}
              />
            </Grid>

            {/* Vale Transporte */}
            <Grid size={{ xs: 12 }}>
              <Controller
                name="vt_enabled"
                control={control}
                render={({ field }) => (
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={(e) => {
                        field.onChange(e.target.checked)
                      }}
                    />
                    <Typography sx={{ ml: 1 }}>
                      Recebe Vale Transporte
                    </Typography>
                  </Box>
                )}
              />
            </Grid>

            {vtEnabled && (
              <>
                <Grid size={{ xs: 6 }}>
                  <Controller
                    name="vt_fare"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Tarifa (R$)"
                        fullWidth
                        placeholder="4.60"
                      />
                    )}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Controller
                    name="vt_trips_per_day"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Viagens/Dia"
                        type="number"
                        fullWidth
                        value={field.value || ''}
                        onChange={(e) =>
                          field.onChange(parseInt(e.target.value) || 0)
                        }
                      />
                    )}
                  />
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>

        <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
          <Button onClick={handleClose}>Cancelar</Button>
          <Button type="submit" variant="contained" disabled={isSubmitting}>
            {provider ? 'Salvar' : 'Criar'}
          </Button>
        </Box>
      </form>
    </Dialog>
  )
}
