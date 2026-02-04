import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  MenuItem,
  IconButton,
  Grid,
  Card,
  Container,
} from '@mui/material'
import {
  Add,
  Edit,
  Delete,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { GenericTable } from '../components/GenericTable'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useSnackbar } from 'notistack'
import {
  getProviders,
  createProvider,
  deleteProvider,
  updateProvider,
} from '../services/api'
import type { Provider } from '../types'
import {
  validateCPF,
  validateCNPJ,
  onlyLetters,
  validateEmail,
  isPositiveNumber,
} from '../utils/validators'
import { CPFInput } from '../components/InputMasks'

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

    // VT (Vale Transporte) fields
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

type ProviderFormInputs = z.infer<typeof providerSchema>

const Providers = () => {
  const [open, setOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchTerm, setSearchTerm] = useState('')
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()

  const isEditMode = editingProvider !== null

  const { data: providersData, isLoading } = useQuery({
    queryKey: ['providers', page, rowsPerPage],
    queryFn: () => getProviders({ page: page + 1, page_size: rowsPerPage }),
  })

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleCloseDialog()
      enqueueSnackbar('Provider created successfully', { variant: 'success' })
    },
    onError: () =>
      enqueueSnackbar('Error creating provider', { variant: 'error' }),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Provider> }) =>
      updateProvider(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleCloseDialog()
      enqueueSnackbar('Provider updated successfully', { variant: 'success' })
    },
    onError: () =>
      enqueueSnackbar('Error updating provider', { variant: 'error' }),
  })

  // Placeholder mutations for actions
  const deleteMutation = useMutation({
    mutationFn: deleteProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      enqueueSnackbar('Provider deleted', { variant: 'success' })
    },
  })

  const {
    control,
    handleSubmit,
    watch,
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

  const paymentMethod = watch('payment_method')

  const onSubmit = (data: ProviderFormInputs) => {
    if (isEditMode) {
      updateMutation.mutate({
        id: editingProvider.id,
        data: data as unknown as Partial<Provider>,
      })
    } else {
      createMutation.mutate(data as unknown as Omit<Provider, 'id'>)
    }
  }

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this provider?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleEdit = (provider: Provider) => {
    setEditingProvider(provider)
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
    setOpen(true)
  }

  const handleCloseDialog = () => {
    setOpen(false)
    setEditingProvider(null)
    reset()
  }

  const handleOpenCreateDialog = () => {
    setEditingProvider(null)
    reset()
    setOpen(true)
  }

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
  }

  const handleRowsPerPageChange = (newRowsPerPage: number) => {
    setRowsPerPage(newRowsPerPage)
    setPage(0)
  }

  // Filter providers based on search term
  const filteredProviders = providersData?.results?.filter((provider) => {
    const searchLower = searchTerm.toLowerCase()
    return (
      provider.name.toLowerCase().includes(searchLower) ||
      provider.role.toLowerCase().includes(searchLower)
    )
  })

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          mb: 3,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Typography variant="h4">Providers</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenCreateDialog}
        >
          Add Provider
        </Button>
      </Box>

      {/* Search Field */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          label="Buscar por nome ou cargo"
          variant="outlined"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Digite o nome do colaborador ou cargo..."
        />
      </Box>

      <Card sx={{ p: 2 }}>
        <GenericTable
          data={filteredProviders}
          loading={isLoading}
          keyExtractor={(p) => p.id}
          totalCount={filteredProviders?.length || 0}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
          columns={[
            { id: 'name', label: 'Nome', accessor: 'name' },
            { id: 'role', label: 'Cargo', accessor: 'role' },
            {
              id: 'salary',
              label: 'Salário Base',
              render: (p) => `R$ ${p.monthly_value || '0.00'}`,
            },
            {
              id: 'method',
              label: 'Forma de Pagamento',
              accessor: 'payment_method',
            },
            {
              id: 'vt',
              label: 'Número de vales por dia',
              render: (p) => {
                if (!p.vt_enabled) return '-'
                return `${p.vt_trips_per_day}`
              },
            },
            {
              id: 'actions',
              label: 'Ações',
              align: 'right',
              render: (p) => (
                <>
                  <IconButton size="small" onClick={() => handleEdit(p)}>
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete(p.id)}
                  >
                    <Delete />
                  </IconButton>
                </>
              ),
            },
          ]}
        />
      </Card>

      <Dialog open={open} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {isEditMode ? 'Edit Provider' : 'New Provider'}
        </DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12 }}>
                <Controller
                  name="name"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Name"
                      fullWidth
                      error={!!errors.name}
                      helperText={errors.name?.message}
                    />
                  )}
                />
              </Grid>

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
                          ? 'CPF/CNPJ cannot be changed'
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

              <Grid size={{ xs: 6 }}>
                <Controller
                  name="role"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Role"
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

              <Grid size={{ xs: 12 }}>
                <Controller
                  name="payment_method"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      select
                      label="Payment Method"
                      fullWidth
                    >
                      <MenuItem value="PIX">PIX</MenuItem>
                      <MenuItem value="TED">TED</MenuItem>
                      <MenuItem value="TRANSFER">Bank Transfer</MenuItem>
                    </TextField>
                  )}
                />
              </Grid>

              {paymentMethod === 'PIX' ? (
                <Grid size={{ xs: 12 }}>
                  <Controller
                    name="pix_key"
                    control={control}
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="PIX Key"
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
                          label="Bank Name"
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
                        <TextField {...field} label="Agency" fullWidth />
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
                          label="Account"
                          fullWidth
                          error={!!errors.bank_account}
                          helperText={errors.bank_account?.message}
                        />
                      )}
                    />
                  </Grid>
                </>
              )}

              <Grid size={{ xs: 12 }}>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Email (Optional)"
                      fullWidth
                      error={!!errors.email}
                      helperText={errors.email?.message}
                    />
                  )}
                />
              </Grid>

              {/* VT Configuration */}
              <Grid size={{ xs: 12 }}>
                <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                  🚌 Vale Transporte
                </Typography>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Controller
                  name="vt_enabled"
                  control={control}
                  render={({ field }) => (
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={field.value}
                        onChange={(e) => field.onChange(e.target.checked)}
                      />
                      <Typography sx={{ ml: 1 }}>
                        Recebe Vale Transporte
                      </Typography>
                    </Box>
                  )}
                />
              </Grid>
              {watch('vt_enabled') && (
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
          <Box
            sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}
          >
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained">
              {isEditMode ? 'Update' : 'Create'}
            </Button>
          </Box>
        </form>
      </Dialog>
    </Container>
  )
}

export default Providers
