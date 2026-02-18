import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  IconButton,
  Card,
  Container,
} from '@mui/material'
import { Add, Edit, Delete } from '@mui/icons-material'
import { GenericTable } from 'src/components/table'
import { SearchField } from 'src/components/search'
import { ProviderDialog } from 'src/components/dialogs/ProviderDialog'
import type { ProviderFormInputs } from 'src/components/dialogs/ProviderDialog'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import {
  getProviders,
  createProvider,
  deleteProvider,
  updateProvider,
} from 'src/services/api'
import type { Provider, PaginatedResponse } from 'src/types'

const Providers = () => {
  const [open, setOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchTerm, setSearchTerm] = useState('')

  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()

  // First fetch to get the total count
  const { data: initialData } = useQuery<PaginatedResponse<Provider>>({
    queryKey: ['providers', 'initial'],
    queryFn: () => getProviders({ page: 1, page_size: 10 }),
  })

  // Fetch all providers using the count from the initial fetch
  const { data: providersData, isLoading } = useQuery<
    PaginatedResponse<Provider>
  >({
    queryKey: ['providers', 'all', searchTerm],
    queryFn: () =>
      getProviders({
        page: 1,
        page_size: initialData!.count,
        search: searchTerm,
      }),
    enabled: !!initialData?.count,
  })

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleCloseDialog()
      enqueueSnackbar('Colaborador criado com sucesso', { variant: 'success' })
    },
    onError: () =>
      enqueueSnackbar('Erro ao criar colaborador', { variant: 'error' }),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Provider> }) =>
      updateProvider(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleCloseDialog()
      enqueueSnackbar('Colaborador atualizado com sucesso', {
        variant: 'success',
      })
    },
    onError: () =>
      enqueueSnackbar('Erro ao atualizar colaborador', { variant: 'error' }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      enqueueSnackbar('Colaborador removido', { variant: 'success' })
    },
  })

  const handleSubmit = (data: ProviderFormInputs) => {
    if (editingProvider) {
      updateMutation.mutate({
        id: editingProvider.id,
        data: data as unknown as Partial<Provider>,
      })
    } else {
      createMutation.mutate(data as unknown as Omit<Provider, 'id'>)
    }
  }

  const handleDelete = (id: number) => {
    if (confirm('Tem certeza que deseja remover este colaborador?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleEdit = (provider: Provider) => {
    setEditingProvider(provider)
    setOpen(true)
  }

  const handleCloseDialog = () => {
    setOpen(false)
    setEditingProvider(null)
  }

  const handleOpenCreateDialog = () => {
    setEditingProvider(null)
    setOpen(true)
  }

  // Client-side filtering + pagination
  const filteredProviders = providersData?.results?.filter((provider) => {
    const searchLower = searchTerm.toLowerCase()
    return (
      provider.name.toLowerCase().includes(searchLower) ||
      provider.role.toLowerCase().includes(searchLower)
    )
  })

  const paginatedProviders = filteredProviders?.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  const isSubmitting = createMutation.isPending || updateMutation.isPending

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
        <Typography variant="h4">Colaboradores</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenCreateDialog}
        >
          Adicionar Colaborador
        </Button>
      </Box>

      <Box sx={{ mb: 2 }}>
        <SearchField
          onSearch={setSearchTerm}
          placeholder="Buscar por nome ou cargo..."
          width={300}
        />
      </Box>

      <Card sx={{ p: 2 }}>
        <GenericTable
          data={paginatedProviders}
          loading={isLoading}
          keyExtractor={(p) => p.id}
          totalCount={filteredProviders?.length || 0}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={setPage}
          onRowsPerPageChange={(n) => {
            setRowsPerPage(n)
            setPage(0)
          }}
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
              render: (p) => (p.vt_enabled ? `${p.vt_trips_per_day}` : '-'),
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

      <ProviderDialog
        open={open}
        provider={editingProvider}
        onClose={handleCloseDialog}
        onSubmit={handleSubmit}
        isSubmitting={isSubmitting}
      />
    </Container>
  )
}

export default Providers
