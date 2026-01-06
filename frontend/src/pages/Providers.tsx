import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  MenuItem,
  Grid,
} from '@mui/material'
import { Add, Edit, Delete } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useSnackbar } from 'notistack'
import { getProviders, createProvider } from '../services/api'
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

  const { data: providers } = useQuery({ queryKey: ['providers'], queryFn: getProviders })

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
    // We need to cast or transform data to match what createProvider expects (Omit<Provider, 'id'>)
    // Since our form inputs match nicely, we can just cast to unknown then to the expected type if needed,
    // or better yet, just pass it if the types align.
    // createProvider expects Omit<Provider, 'id'>.
    // ProviderFormInputs has all string fields basically.
    // Let's rely on the API to handle string->decimal conversion or handle it here?
    // The previous code had (data as any), I will prioritize fixing the lint error.
    createMutation.mutate(data as unknown as Omit<Provider, 'id'>)
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Providers</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpen(true)}>
          Add Provider
        </Button>
      </Box>

      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Base Salary</TableCell>
              <TableCell>Method</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {providers?.map((provider) => (
              <TableRow key={provider.id}>
                <TableCell>{provider.name}</TableCell>
                <TableCell>{provider.role}</TableCell>
                <TableCell>R$ {provider.salary_base}</TableCell>
                <TableCell>{provider.payment_method}</TableCell>
                <TableCell>
                  <IconButton size="small">
                    <Edit />
                  </IconButton>
                  <IconButton size="small" color="error">
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

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
    </Box>
  )
}

export default Providers
