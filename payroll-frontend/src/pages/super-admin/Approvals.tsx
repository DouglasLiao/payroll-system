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
  Button,
  CircularProgress,
} from '@mui/material'
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
} from '../../services/superAdminApi'

const Approvals = () => {
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['pendingCompanies'],
    queryFn: () => getCompanies({ is_active: false, page_size: 100 }),
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
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          Aprovações Pendentes
        </Typography>
        <Typography color="textSecondary">
          Empresas que se cadastraram e aguardam liberação.
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Empresa</TableCell>
              <TableCell>CNPJ</TableCell>
              <TableCell>Telefone</TableCell>
              <TableCell>Data Cadastro</TableCell>
              <TableCell align="right">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : pendingCompanies.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <Typography color="textSecondary">
                    Nenhuma solicitação pendente.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              pendingCompanies.map((company) => (
                <TableRow key={company.id}>
                  <TableCell>
                    <Typography variant="subtitle2">{company.name}</Typography>
                    <Typography variant="caption" color="textSecondary">
                      {company.email}
                    </Typography>
                  </TableCell>
                  <TableCell>{company.cnpj}</TableCell>
                  <TableCell>{company.phone || '-'}</TableCell>
                  <TableCell>
                    {new Date(company.created_at).toLocaleDateString('pt-BR')}
                  </TableCell>
                  <TableCell align="right">
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

export default Approvals
