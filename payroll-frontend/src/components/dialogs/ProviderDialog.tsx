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
import { useEffect, useState } from 'react'
import { CustomMenuItem } from './CustomMenuItem'
import { CPFInput } from './InputMasks'
import {
  validateCPF,
  validateCNPJ,
  onlyLetters,
  validateEmail,
  isPositiveNumber,
} from '../utils/validators'
import type { Provider } from '../types'

// ── Schema ────────────────────────────────────────────────────────────────────

const providerSchema = z
  .object({
    name: z
      .string()
      .min(3, 'Nome deve ter pelo menos 3 caracteres')
      .max(100, 'Nome muito longo')
      .refine(onlyLetters, 'Nome deve conter apenas letras e espaços'),

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

    pix_key: z.string().optional(),
    bank_name: z.string().optional(),
    bank_agency: z.string().optional(),
    bank_account: z.string().optional(),

    email: z
      .string()
      .optional()
      .refine((val) => !val || validateEmail(val), 'Email inválido')
      .or(z.literal('')),

    description: z.string().max(500, 'Descrição muito longa').optional(),

    vt_enabled: z.boolean().optional(),
    vt_fare: z.string().optional(),
    vt_trips_per_day: z.number().min(0).optional(),
  })
  .refine(
    (data) => {
      if (data.payment_method === 'PIX' && !data.pix_key) return false
      return true
    },
    {
      message: 'Chave PIX é obrigatória para pagamento via PIX',
      path: ['pix_key'],
    }
  )
  .refine(
    (data) => {
      if (
        data.payment_method !== 'PIX' &&
        (!data.bank_name || !data.bank_account)
      )
        return false
      return true
    },
    {
      message: 'Dados bancários são obrigatórios para TED/Transferência',
      path: ['bank_name'],
    }
  )

export type ProviderFormInputs = z.infer<typeof providerSchema>

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
  const isEditMode = provider != null
  const [paymentMethod, setPaymentMethod] = useState<
    'PIX' | 'TED' | 'TRANSFER'
  >('PIX')
  const [vtEnabled, setVtEnabled] = useState(false)

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProviderFormInputs>({
    resolver: zodResolver(providerSchema),
    defaultValues: {
      name: '',
      document: '',
      role: '',
      monthly_value: '',
      payment_method: 'PIX',
      pix_key: '',
      bank_name: '',
      bank_agency: '',
      bank_account: '',
      email: '',
      description: '',
      vt_enabled: false,
      vt_fare: '4.60',
      vt_trips_per_day: 4,
    },
  })

  // Populate form when editing
  useEffect(() => {
    if (provider) {
      setPaymentMethod(provider.payment_method)
      setVtEnabled(provider.vt_enabled || false)
      reset({
        name: provider.name,
        role: provider.role,
        monthly_value: provider.monthly_value,
        payment_method: provider.payment_method,
        pix_key: provider.pix_key || '',
        bank_name: provider.bank_name || '',
        bank_agency: provider.bank_agency || '',
        bank_account: provider.bank_account || '',
        email: provider.email || '',
        description: provider.description || '',
        vt_enabled: provider.vt_enabled || false,
        vt_fare: provider.vt_fare || '4.60',
        vt_trips_per_day: provider.vt_trips_per_day || 4,
      })
    } else {
      setPaymentMethod('PIX')
      setVtEnabled(false)
      reset()
    }
  }, [provider, reset])

  const handleClose = () => {
    reset()
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {isEditMode ? 'Editar Colaborador' : 'Novo Colaborador'}
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
                    disabled={isEditMode}
                    error={!!fieldState.error}
                    helperText={
                      isEditMode
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
                    onChange={(e) => {
                      field.onChange(e)
                      setPaymentMethod(
                        e.target.value as 'PIX' | 'TED' | 'TRANSFER'
                      )
                    }}
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

            {/* PIX ou Dados Bancários */}
            {paymentMethod === 'PIX' ? (
              <Grid size={{ xs: 12 }}>
                <Controller
                  name="pix_key"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Chave PIX"
                      fullWidth
                      error={!!errors.pix_key}
                      helperText={errors.pix_key?.message}
                    />
                  )}
                />
              </Grid>
            ) : (
              <>
                <Grid size={{ xs: 12 }}>
                  <Controller
                    name="bank_name"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Nome do Banco"
                        fullWidth
                        error={!!errors.bank_name}
                        helperText={errors.bank_name?.message}
                      />
                    )}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Controller
                    name="bank_agency"
                    control={control}
                    render={({ field }) => (
                      <TextField {...field} label="Agência" fullWidth />
                    )}
                  />
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <Controller
                    name="bank_account"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Conta"
                        fullWidth
                        error={!!errors.bank_account}
                        helperText={errors.bank_account?.message}
                      />
                    )}
                  />
                </Grid>
              </>
            )}

            {/* Email */}
            <Grid size={{ xs: 12 }}>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Email (Opcional)"
                    fullWidth
                    error={!!errors.email}
                    helperText={errors.email?.message}
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
                        setVtEnabled(e.target.checked)
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
            {isEditMode ? 'Salvar' : 'Criar'}
          </Button>
        </Box>
      </form>
    </Dialog>
  )
}
