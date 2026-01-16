import { useState } from 'react'
import { Box, Typography, Button, Container } from '@mui/material'
import { Add, Visibility } from '@mui/icons-material'
import { GenericTable } from '../components/GenericTable'
import { StatusChip } from '../components/StatusChip'
import {
  PayrollFiltersComponent,
  type PayrollFilters,
} from '../components/PayrollFilters'
import { PayrollFormDialog } from '../components/PayrollFormDialog'
import { PayrollDetailDialog } from '../components/PayrollDetailDialog'
import { PayrollStats } from '../components/PayrollStats'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import type { Payroll, PayrollCreateData } from '../types'
import { formatCurrency } from '../utils/formatters'
import {
  getPayrolls,
  getProviders,
  createPayroll,
  getPayrollDetail,
  closePayroll,
  markPayrollAsPaid,
  downloadPayrollExcel,
} from '../services/api'

const Payrolls = () => {
  const [openForm, setOpenForm] = useState(false)
  const [openDetail, setOpenDetail] = useState(false)
  const [selectedPayroll, setSelectedPayroll] = useState<number | null>(null)
  const [filters, setFilters] = useState<PayrollFilters>({
    status: 'all',
    reference_month: '',
  })

  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()

  const { data: payrolls, isLoading } = useQuery({
    queryKey: ['payrolls', filters],
    queryFn: () => getPayrolls(filters),
  })

  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  const { data: payrollDetail } = useQuery({
    queryKey: ['payroll-detail', selectedPayroll],
    queryFn: () => getPayrollDetail(selectedPayroll!),
    enabled: !!selectedPayroll && openDetail,
  })

  const createMutation = useMutation({
    mutationFn: createPayroll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      setOpenForm(false)
      enqueueSnackbar('Folha criada com sucesso!', { variant: 'success' })
    },
    onError: (error: Error) =>
      enqueueSnackbar(error.message, { variant: 'error' }),
  })

  const closeMutation = useMutation({
    mutationFn: closePayroll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      queryClient.invalidateQueries({ queryKey: ['payroll-detail'] })
      enqueueSnackbar('Folha fechada com sucesso!', { variant: 'success' })
    },
  })

  const markPaidMutation = useMutation({
    mutationFn: markPayrollAsPaid,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      queryClient.invalidateQueries({ queryKey: ['payroll-detail'] })
      enqueueSnackbar('Folha marcada como paga!', { variant: 'success' })
    },
  })

  const handleCreateSubmit = (data: PayrollCreateData) => {
    createMutation.mutate(data)
  }

  const handleViewDetails = (payroll: Payroll) => {
    setSelectedPayroll(payroll.id)
    setOpenDetail(true)
  }

  const handleDownloadExcel = async (payrollId: number) => {
    try {
      await downloadPayrollExcel(payrollId)
      enqueueSnackbar('Excel baixado com sucesso!', { variant: 'success' })
    } catch {
      enqueueSnackbar('Erro ao baixar Excel', { variant: 'error' })
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Folhas de Pagamento</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenForm(true)}
        >
          Nova Folha
        </Button>
      </Box>

      {/* Stats Cards */}
      <PayrollStats payrolls={payrolls} isLoading={isLoading} />

      {/* Filters */}
      <PayrollFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        providers={providers}
      />

      {/* Table */}
      <GenericTable<Payroll>
        data={payrolls}
        loading={isLoading}
        keyExtractor={(p) => p.id}
        columns={[
          { id: 'provider', label: 'Prestador', accessor: 'provider_name' },
          { id: 'month', label: 'Mês', accessor: 'reference_month' },
          {
            id: 'status',
            label: 'Status',
            render: (p) => (
              <StatusChip
                status={p.status as 'DRAFT' | 'CLOSED' | 'PAID'}
                label={p.status_display}
              />
            ),
          },
          {
            id: 'base',
            label: 'Base',
            align: 'right',
            render: (p) => formatCurrency(p.base_value),
          },
          {
            id: 'earnings',
            label: 'Proventos',
            align: 'right',
            render: (p) => (
              <Box sx={{ color: 'success.main' }}>
                +{formatCurrency(p.total_earnings)}
              </Box>
            ),
          },
          {
            id: 'discounts',
            label: 'Descontos',
            align: 'right',
            render: (p) => (
              <Box sx={{ color: 'error.main' }}>
                -{formatCurrency(p.total_discounts)}
              </Box>
            ),
          },
          {
            id: 'net',
            label: 'Líquido',
            align: 'right',
            render: (p) => (
              <Typography fontWeight={700}>
                {formatCurrency(p.net_value)}
              </Typography>
            ),
          },
          {
            id: 'actions',
            label: 'Ações',
            align: 'right',
            render: (p) => (
              <Button
                size="small"
                startIcon={<Visibility />}
                onClick={() => handleViewDetails(p)}
              >
                Ver
              </Button>
            ),
          },
        ]}
      />

      {/* Form Dialog */}
      <PayrollFormDialog
        open={openForm}
        onClose={() => setOpenForm(false)}
        onSubmit={handleCreateSubmit}
        providers={providers}
        isPending={createMutation.isPending}
      />

      {/* Detail Dialog */}
      <PayrollDetailDialog
        open={openDetail}
        onClose={() => setOpenDetail(false)}
        payrollDetail={payrollDetail}
        onMarkPaid={(id) => markPaidMutation.mutate(id)}
        onDownloadExcel={handleDownloadExcel}
        isMarkingPaid={markPaidMutation.isPending}
        isClosing={closeMutation.isPending}
      />
    </Container>
  )
}

export default Payrolls
