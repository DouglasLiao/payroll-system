import { Box, Typography, Chip, type ChipProps } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getAllSubscriptions } from '../../services/superAdminApi'
import { GenericTable } from '../../components/table'
import { useState } from 'react'

const Subscriptions = () => {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  const { data, isLoading } = useQuery({
    queryKey: ['allSubscriptions', page], // API uses page, but not rowsPerPage yet?
    // getAllSubscriptions accepts page.
    // Let's assume we pass page + 1. RowsPerPage might be fixed or I need to check API.
    // Looking at `superAdminApi.ts`: `getAllSubscriptions = async (page = 1) => ...`
    // It doesn't seem to accept page_size currently, but I'll add it if I can or adhere to existing.
    // I'll stick to page for now.
    queryFn: () => getAllSubscriptions(page + 1),
  })

  // getStatusColor remains the same
  const getStatusColor = (status: string): ChipProps['color'] => {
    switch (status) {
      case 'Ativa':
        return 'success'
      case 'Inativa':
        return 'error'
      case 'Expirada':
        return 'warning'
      default:
        return 'default'
    }
  }

  const subscriptions = data?.results || []

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
        Assinaturas
      </Typography>

      <GenericTable
        data={subscriptions}
        loading={isLoading}
        keyExtractor={(sub) => sub.id}
        totalCount={data?.count || 0}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={setPage}
        onRowsPerPageChange={(newRows) => {
          setRowsPerPage(newRows)
          setPage(0)
        }}
        columns={[
          { id: 'company_name', label: 'Empresa', accessor: 'company_name' },
          {
            id: 'plan_type',
            label: 'Plano',
            render: (sub) => (
              <Chip
                label={sub.plan_type_display}
                size="small"
                color="primary"
                variant="outlined"
              />
            ),
          },
          {
            id: 'max_providers',
            label: 'Limite Prestadores',
            render: (sub) =>
              sub.max_providers === null ? 'Ilimitado' : sub.max_providers,
          },
          {
            id: 'price',
            label: 'Preço',
            render: (sub) =>
              new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
              }).format(Number(sub.price)),
          },
          {
            id: 'end_date',
            label: 'Vencimento',
            render: (sub) =>
              sub.end_date
                ? new Date(sub.end_date).toLocaleDateString('pt-BR')
                : 'Vitalício',
          },
          {
            id: 'status',
            label: 'Status',
            render: (sub) => (
              <Chip
                label={sub.status_display}
                color={getStatusColor(sub.status_display)}
                size="small"
              />
            ),
          },
        ]}
      />
    </Box>
  )
}

export default Subscriptions
