import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material'
import { CustomMenuItem } from '../../components/menu'
import {
  Visibility as ViewIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material'
import { GenericTable } from '../../components/table'
import { useQuery } from '@tanstack/react-query'
import api from '../../services/authApi'

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
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

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

  const paginatedPayrolls = payrolls.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

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
                <CustomMenuItem value="">Todos</CustomMenuItem>
                <CustomMenuItem value="01/2026">Janeiro/2026</CustomMenuItem>
                <CustomMenuItem value="02/2026">Fevereiro/2026</CustomMenuItem>
                <CustomMenuItem value="03/2026">Março/2026</CustomMenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
              >
                <CustomMenuItem value="">Todos</CustomMenuItem>
                <CustomMenuItem value="DRAFT">Rascunho</CustomMenuItem>
                <CustomMenuItem value="CLOSED">Fechado</CustomMenuItem>
                <CustomMenuItem value="PAID">Pago</CustomMenuItem>
              </Select>
            </FormControl>
          </Box>
        </CardContent>
      </Card>

      {/* Payrolls Table */}
      <GenericTable
        data={paginatedPayrolls}
        loading={isLoading}
        keyExtractor={(p) => p.id}
        totalCount={payrolls.length}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={setPage}
        onRowsPerPageChange={(newRows) => {
          setRowsPerPage(newRows)
          setPage(0)
        }}
        columns={[
          {
            id: 'reference',
            label: 'Referência',
            render: (p) => (
              <Typography variant="body2" fontWeight={500}>
                {p.reference_month}
              </Typography>
            ),
          },
          { id: 'provider', label: 'Colaborador', accessor: 'provider_name' },
          {
            id: 'net_value',
            label: 'Valor Líquido',
            align: 'right',
            render: (p) => (
              <Typography variant="body2" fontWeight={600} color="primary">
                {formatCurrency(p.net_value)}
              </Typography>
            ),
          },
          {
            id: 'status',
            label: 'Status',
            align: 'center',
            render: (p) => (
              <Chip
                label={p.status_display}
                color={
                  getStatusColor(p.status) as
                    | 'default'
                    | 'primary'
                    | 'secondary'
                    | 'error'
                    | 'info'
                    | 'success'
                    | 'warning'
                }
                size="small"
              />
            ),
          },
          {
            id: 'date',
            label: 'Data',
            align: 'center',
            render: (p) => (
              <Typography variant="caption">
                {new Date(p.created_at).toLocaleDateString('pt-BR')}
              </Typography>
            ),
          },
          {
            id: 'actions',
            label: 'Ações',
            align: 'right',
            render: (p) => (
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <IconButton size="small" onClick={() => setSelectedPayroll(p)}>
                  <ViewIcon />
                </IconButton>
                <IconButton size="small" onClick={() => handleDownload(p.id)}>
                  <DownloadIcon />
                </IconButton>
              </Box>
            ),
          },
        ]}
      />

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
