import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import {
  Visibility as ViewIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import api from '../services/authApi'

interface Payroll {
  id: number
  provider_name: string
  reference_month: string
  status: string
  status_display: string
  net_value: string
  created_at: string
}

export default function ProviderPayments() {
  const [selectedPayroll, setSelectedPayroll] = useState<Payroll | null>(null)
  const [filterMonth, setFilterMonth] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  // Fetch payrolls
  const { data: payrolls = [], isLoading } = useQuery({
    queryKey: ['provider-payrolls', filterMonth, filterStatus],
    queryFn: async () => {
      let url = '/payrolls/'
      const params = new URLSearchParams()

      if (filterMonth) params.append('reference_month', filterMonth)
      if (filterStatus) params.append('status', filterStatus)

      if (params.toString()) url += `?${params.toString()}`

      const response = await api.get<{ results: Payroll[] }>(url)
      return response.data.results || response.data
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DRAFT':
        return 'default'
      case 'CLOSED':
        return 'warning'
      case 'PAID':
        return 'success'
      default:
        return 'default'
    }
  }

  const formatCurrency = (value: string) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(parseFloat(value))
  }

  const handleDownload = async (payrollId: number) => {
    try {
      const response = await api.get(`/payrolls/${payrollId}/export-excel/`, {
        responseType: 'blob',
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `payroll_${payrollId}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Erro ao baixar:', error)
    }
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Meus Pagamentos
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Visualize seus recibos de pagamento
        </Typography>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FilterIcon />
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Mês de Referência</InputLabel>
              <Select
                value={filterMonth}
                onChange={(e) => setFilterMonth(e.target.value)}
                label="Mês de Referência"
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="01/2026">Janeiro/2026</MenuItem>
                <MenuItem value="02/2026">Fevereiro/2026</MenuItem>
                <MenuItem value="03/2026">Março/2026</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="DRAFT">Rascunho</MenuItem>
                <MenuItem value="CLOSED">Fechado</MenuItem>
                <MenuItem value="PAID">Pago</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </CardContent>
      </Card>

      {/* Payrolls Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Referência</TableCell>
              <TableCell>Colaborador</TableCell>
              <TableCell align="right">Valor Líquido</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Data</TableCell>
              <TableCell align="right">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : payrolls.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  Nenhum pagamento encontrado
                </TableCell>
              </TableRow>
            ) : (
              payrolls.map((payroll) => (
                <TableRow key={payroll.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {payroll.reference_month}
                    </Typography>
                  </TableCell>
                  <TableCell>{payroll.provider_name}</TableCell>
                  <TableCell align="right">
                    <Typography
                      variant="body2"
                      fontWeight={600}
                      color="primary"
                    >
                      {formatCurrency(payroll.net_value)}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={payroll.status_display}
                      color={getStatusColor(payroll.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="caption">
                      {new Date(payroll.created_at).toLocaleDateString('pt-BR')}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => setSelectedPayroll(payroll)}
                    >
                      <ViewIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDownload(payroll.id)}
                    >
                      <DownloadIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Details Dialog */}
      <Dialog
        open={!!selectedPayroll}
        onClose={() => setSelectedPayroll(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Detalhes do Pagamento - {selectedPayroll?.reference_month}
        </DialogTitle>
        <DialogContent>
          {selectedPayroll && (
            <Box sx={{ pt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {selectedPayroll.provider_name}
              </Typography>
              <Box
                sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}
              >
                <Typography>Status:</Typography>
                <Chip
                  label={selectedPayroll.status_display}
                  color={getStatusColor(selectedPayroll.status)}
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="h6">Valor Líquido:</Typography>
                <Typography variant="h6" color="primary">
                  {formatCurrency(selectedPayroll.net_value)}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  )
}
