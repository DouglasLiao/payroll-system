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
import { Add, Edit, Delete } from '@mui/icons-material'
import { GenericTable } from '../components/GenericTable'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useSnackbar } from 'notistack'
import { getProviders, createProvider, deleteProvider } from '../services/api'
import type { Provider } from '../types'

const providerSchema = z
  .object({
    name: z.string().min(3, 'Name is required'),
    role: z.string().min(2, 'Role is required'),
    salary_base: z.string().min(1, 'Salary is required'), // Decimal as string input
    payment_method: z.enum(['PIX', 'TED', 'TRANSFER']),
    pix_key: z.string().optional(),
    bank_name: z.string().optional(),
    bank_agency: z.string().optional(),
    bank_account: z.string().optional(),
    email: z.string().email().optional().or(z.literal('')),
    description: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.payment_method === 'PIX' && !data.pix_key) return false
      if (data.payment_method !== 'PIX' && (!data.bank_name || !data.bank_account)) return false
      return true
    },
    {
      message: 'Banking details are required for the selected method',
      path: ['payment_method'], // Attach error to payment_method or specific fields ideally
    }
  )

type ProviderFormInputs = z.infer<typeof providerSchema>

const Providers = () => {
  const [open, setOpen] = useState(false)
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()

  const { data: providers, isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      setOpen(false)
      enqueueSnackbar('Provider created successfully', { variant: 'success' })
      reset()
    },
    onError: () => enqueueSnackbar('Error creating provider', { variant: 'error' }),
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
      role: '',
      salary_base: '',
      payment_method: 'PIX',
      pix_key: '',
      bank_name: '',
      bank_agency: '',
      bank_account: '',
      email: '',
      description: '',
    },
  })

  const paymentMethod = watch('payment_method')

  const onSubmit = (data: ProviderFormInputs) => {
    createMutation.mutate(data as unknown as Omit<Provider, 'id'>)
  }

  const handleDelete = (id: number) => {
    if (confirm('Are you sure?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleEdit = (provider: Provider) => {
    console.log('Edit', provider)
    // TODO: Implement Edit logic (populate form, set edit mode)
  }

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h4">Providers</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>
          Add Provider
        </Button>
      </Box>

      <Card sx={{ p: 2 }}>
        <GenericTable
          data={providers}
          loading={isLoading}
          keyExtractor={(p) => p.id}
          columns={[
            { id: 'name', label: 'Name', accessor: 'name' },
            { id: 'role', label: 'Role', accessor: 'role' },
            {
              id: 'salary',
              label: 'Base Salary',
              render: (p) => `R$ ${p.monthly_value || '0.00'}`,
            },
            { id: 'method', label: 'Method', accessor: 'payment_method' },
            {
              id: 'actions',
              label: 'Actions',
              align: 'right',
              render: (p) => (
                <>
                  <IconButton size="small" onClick={() => handleEdit(p)}>
                    <Edit />
                  </IconButton>
                  <IconButton size="small" color="error" onClick={() => handleDelete(p.id)}>
                    <Delete />
                  </IconButton>
                </>
              ),
            },
          ]}
        />
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Provider</DialogTitle>
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
                  name="salary_base"
                  control={control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      label="Base Salary"
                      fullWidth
                      error={!!errors.salary_base}
                      helperText={errors.salary_base?.message}
                    />
                  )}
                />
              </Grid>

              <Grid size={{ xs: 12 }}>
                <Controller
                  name="payment_method"
                  control={control}
                  render={({ field }) => (
                    <TextField {...field} select label="Payment Method" fullWidth>
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
                      render={({ field }) => <TextField {...field} label="Agency" fullWidth />}
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
            </Grid>
          </DialogContent>
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button onClick={() => setOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">
              Create
            </Button>
          </Box>
        </form>
      </Dialog>
    </Container>
  )
}

export default Providers
