import { Box, Typography, Button } from '@mui/material'
import { useState } from 'react'
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import {
  getCompanies,
  approveCompany,
  rejectCompany,
} from 'src/services/superAdminApi'
import { SearchField } from 'src/components/search'
import { GenericTable } from 'src/components/table'

const Approvals = () => {
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  const { data, isLoading } = useQuery({
    queryKey: ['pendingCompanies', search, page, rowsPerPage],
    queryFn: () =>
      getCompanies({
        is_active: false,
        page: page + 1,
        page_size: rowsPerPage,
        search,
      }),
  })

  const pendingCompanies = data?.results || []

  const approveMutation = useMutation({
    mutationFn: approveCompany,
    onSuccess: () => {
      enqueueSnackbar('Empresa aprovada com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['pendingCompanies'] })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      queryClient.invalidateQueries({ queryKey: ['superAdminStats'] })
    },
    onError: () => {
      enqueueSnackbar('Erro ao aprovar empresa.', { variant: 'error' })
    },
  })

  const handleApprove = (id: number) => {
    if (confirm('Deseja aprovar esta empresa e ativar sua assinatura?')) {
      approveMutation.mutate(id)
    }
  }

  const rejectMutation = useMutation({
    mutationFn: rejectCompany,
    onSuccess: () => {
      enqueueSnackbar('Empresa rejeitada com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['pendingCompanies'] })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      queryClient.invalidateQueries({ queryKey: ['superAdminStats'] })
    },
    onError: () => {
      enqueueSnackbar('Erro ao rejeitar empresa.', { variant: 'error' })
    },
  })

  const handleReject = (id: number) => {
    if (
      confirm(
        'Tem certeza que deseja REJEITAR esta empresa? Os dados serão excluídos permanentemente.'
      )
    ) {
      rejectMutation.mutate(id)
    }
  }

  return (
    <Box>
      <Box
        sx={{
          mb: 4,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Box>
          <Typography variant="h4" fontWeight="bold">
            Aprovações Pendentes
          </Typography>
          <Typography color="textSecondary">
            Empresas que se cadastraram e aguardam liberação.
          </Typography>
        </Box>
        <SearchField
          onSearch={setSearch}
          placeholder="Buscar empresa..."
          width={300}
        />
      </Box>

      <GenericTable
        data={pendingCompanies}
        loading={isLoading}
        keyExtractor={(company) => company.id}
        totalCount={data?.count || 0}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={setPage}
        onRowsPerPageChange={(newRows) => {
          setRowsPerPage(newRows)
          setPage(0)
        }}
        columns={[
          {
            id: 'name',
            label: 'Empresa',
            render: (company) => (
              <Box>
                <Typography variant="subtitle2">{company.name}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {company.email}
                </Typography>
              </Box>
            ),
          },
          { id: 'cnpj', label: 'CNPJ', accessor: 'cnpj' },
          {
            id: 'phone',
            label: 'Telefone',
            render: (company) => company.phone || '-',
          },
          {
            id: 'created_at',
            label: 'Data Cadastro',
            render: (company) =>
              new Date(company.created_at).toLocaleDateString('pt-BR'),
          },
          {
            id: 'actions',
            label: 'Ações',
            align: 'right',
            render: (company) => (
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  startIcon={<CancelIcon />}
                  onClick={() => handleReject(company.id)}
                  disabled={
                    rejectMutation.isPending || approveMutation.isPending
                  }
                  sx={{ mr: 1 }}
                >
                  Rejeitar
                </Button>
                <Button
                  variant="contained"
                  color="success"
                  size="small"
                  startIcon={<CheckIcon />}
                  onClick={() => handleApprove(company.id)}
                  disabled={approveMutation.isPending}
                >
                  Aprovar
                </Button>
              </Box>
            ),
          },
        ]}
      />
    </Box>
  )
}

export default Approvals
