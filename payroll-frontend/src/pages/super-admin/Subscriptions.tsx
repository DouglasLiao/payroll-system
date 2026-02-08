import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  type ChipProps,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getAllSubscriptions } from '../../services/superAdminApi'

const Subscriptions = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['allSubscriptions'],
    queryFn: () => getAllSubscriptions(1), // Page 1
  })

  const subscriptions = data?.results || []

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

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
        Assinaturas
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Empresa</TableCell>
              <TableCell>Plano</TableCell>
              <TableCell>Limite Prestadores</TableCell>
              <TableCell>Preço</TableCell>
              <TableCell>Vencimento</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : subscriptions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Nenhuma assinatura encontrada
                </TableCell>
              </TableRow>
            ) : (
              subscriptions.map((sub) => (
                <TableRow key={sub.id}>
                  <TableCell>{sub.company_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={sub.plan_type_display}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    {sub.max_providers === null
                      ? 'Ilimitado'
                      : sub.max_providers}
                  </TableCell>
                  <TableCell>
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL',
                    }).format(Number(sub.price))}
                  </TableCell>
                  <TableCell>
                    {sub.end_date
                      ? new Date(sub.end_date).toLocaleDateString('pt-BR')
                      : 'Vitalício'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={sub.status_display}
                      color={getStatusColor(sub.status_display)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default Subscriptions
