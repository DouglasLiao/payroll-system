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
import { GenericTable, type Column } from 'src/components/table'
import { SearchField } from 'src/components/search'
import { ProviderDialog } from 'src/components/dialogs/ProviderDialog'
import type { ProviderFormInputs } from 'src/components/dialogs/ProviderDialog'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToast } from 'src/hooks/useToast'
import {
  getProviders,
  createProvider,
  deleteProvider,
  updateProvider,
} from 'src/services/api'
import type { Provider } from 'src/types'

const Providers = () => {
  const [open, setOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchTerm, setSearchTerm] = useState('')

  const queryClient = useQueryClient()
  const toast = useToast()

  const { data: providersData, isLoading } = useQuery({
    queryKey: ['providers', page, rowsPerPage, searchTerm],
    queryFn: () =>
      getProviders({
        page: page + 1,
        page_size: rowsPerPage,
        search: searchTerm,
      }),
  })

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleCloseDialog()
      toast.success('Colaborador criado com sucesso')
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail ||
        error.response?.data?.[0] ||
        (Array.isArray(error.response?.data)
          ? error.response?.data[0]
          : null) ||
        'Erro ao criar colaborador'
      toast.error(message)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Provider> }) =>
      updateProvider(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleCloseDialog()
      toast.success('Colaborador atualizado com sucesso')
    },
    onError: () => toast.error('Erro ao atualizar colaborador'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProvider,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      toast.success('Colaborador removido')
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

  const rawList: Provider[] =
    (providersData as any)?.results ||
    (Array.isArray(providersData) ? providersData : [])

  const listCount = (providersData as any)?.count || rawList.length

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
          onSearch={(val) => {
            setSearchTerm(val)
            setPage(0)
          }}
          placeholder="Buscar por nome ou cargo..."
          width={300}
        />
      </Box>

      <Card sx={{ p: 2 }}>
        <GenericTable<Provider>
          data={rawList}
          loading={isLoading}
          keyExtractor={(p) => p.id}
          totalCount={listCount}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={setPage}
          onRowsPerPageChange={(n) => {
            setRowsPerPage(n)
            setPage(0)
          }}
          columns={
            [
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
            ] as Column<Provider>[]
          }
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
