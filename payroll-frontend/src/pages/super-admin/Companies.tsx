import { useState } from 'react'
import { Box, Typography, IconButton } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import {
  Delete as DeleteIcon,
  Business as BusinessIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getCompanies } from '../../services/superAdminApi'
import api from '../../services/authApi' // Keep for create-admin specific call or move to superAdminApi
import { enqueueSnackbar } from 'notistack'
import { GenericTable, type Column } from '../../components/table'
import { SearchField } from '../../components/search'

export default function Companies() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [search, setSearch] = useState('')

  // Fetch companies
  const { data, isLoading } = useQuery({
    queryKey: ['companies', page, rowsPerPage, search],
    queryFn: () =>
      getCompanies({ page: page + 1, page_size: rowsPerPage, search }),
  })

  const companies = data?.results || []

  // Delete company mutation
  const deleteCompanyMutation = useMutation({
    mutationFn: async (id: number) => {
      return await api.delete(`/companies/${id}/`)
    },
    onSuccess: () => {
      enqueueSnackbar('Empresa deletada com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
    onError: () => {
      enqueueSnackbar('Erro ao deletar empresa', { variant: 'error' })
    },
  })

  const handleDeleteCompany = (id: number) => {
    if (confirm('Tem certeza que deseja deletar esta empresa?')) {
      deleteCompanyMutation.mutate(id)
    }
  }

  const columns: Column<Company>[] = [
    {
      id: 'name',
      label: 'Empresa',
      render: (company) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BusinessIcon color="primary" />
          <Typography variant="body2" fontWeight={500}>
            {company.name}
          </Typography>
        </Box>
      ),
    },
    {
      id: 'cnpj',
      label: 'CNPJ',
      accessor: 'cnpj',
    },
    {
      id: 'start_date',
      label: 'Data de Início',
      render: (company) => new Date(company.created_at).toLocaleDateString(),
    },
    {
      id: 'license',
      label: 'Licença',
      render: (company) =>
        company.subscription_end_date
          ? new Date(company.subscription_end_date).toLocaleDateString()
          : '-',
    },
    {
      id: 'edit',
      label: 'Editar',
      align: 'center',
      render: (company) => (
        <IconButton
          size="small"
          color="primary"
          title="Configurações"
          onClick={() =>
            navigate(`/super-admin/companies/${company.id}/config`)
          }
        >
          <SettingsIcon fontSize="small" />
        </IconButton>
      ),
    },
    {
      id: 'actions',
      label: 'Deleção',
      align: 'right',
      render: (company) => (
        <IconButton
          size="small"
          color="error"
          onClick={() => handleDeleteCompany(company.id)}
          disabled={company.id === 1}
        >
          <DeleteIcon />
        </IconButton>
      ),
    },
  ]

  return (
    <Box>
      <Box
        sx={{
          mb: 3,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="h4" fontWeight="bold">
          Gerenciamento de Empresas
        </Typography>
        <SearchField
          onSearch={setSearch}
          placeholder="Buscar por nome ou CNPJ..."
          width={300}
        />
      </Box>

      <GenericTable
        data={companies}
        columns={columns}
        keyExtractor={(item) => item.id}
        loading={isLoading}
        totalCount={data?.count || 0}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={(newPage) => setPage(newPage)}
        onRowsPerPageChange={(newRowsPerPage) => {
          setRowsPerPage(newRowsPerPage)
          setPage(0)
        }}
        rowsPerPageOptions={[10, 25, 50, 100]}
        emptyMessage="Nenhuma empresa cadastrada"
      />
    </Box>
  )
}
