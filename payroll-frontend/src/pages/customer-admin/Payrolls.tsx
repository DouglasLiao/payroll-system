import { useState } from 'react'
import { Box, Typography, Button, Container } from '@mui/material'
import { Add, Visibility } from '@mui/icons-material'
import { GenericTable } from '../../components/GenericTable'
import { StatusChip } from '../../components/StatusChip'
import {
  PayrollFiltersComponent,
  type PayrollFilters,
} from '../../components/PayrollFilters'
import { PayrollFormDialog } from '../../components/PayrollFormDialog'
import { PayrollDetailDialog } from '../../components/PayrollDetailDialog'
import { PayrollStats } from '../../components/PayrollStats'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import type {
  Payroll,
  PayrollCreateData,
  PayrollDetail,
  PaginatedResponse,
} from '../../types'
import { formatCurrency } from '../../utils/formatters'
import {
  getPayrolls,
  getProviders,
  createPayroll,
  getPayrollDetail,
  closePayroll,
  markPayrollAsPaid,
  reopenPayroll,
  updatePayroll,
  downloadPayrollFile,
} from '../../services/api'

const Payrolls = () => {
  const [openForm, setOpenForm] = useState(false)
  const [openDetail, setOpenDetail] = useState(false)
  const [selectedPayroll, setSelectedPayroll] = useState<number | null>(null)
  const [editingPayroll, setEditingPayroll] = useState<PayrollDetail | null>(
    null
  )
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [filters, setFilters] = useState<PayrollFilters>({
    status: 'all',
    reference_month: '',
  })

  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()

  const { data: payrollsData, isLoading } = useQuery({
    queryKey: ['payrolls', filters, page, rowsPerPage],
    queryFn: () =>
      getPayrolls({ ...filters, page: page + 1, page_size: rowsPerPage }),
  })

  const { data: providersData } = useQuery({
    queryKey: ['providers'],
    queryFn: () => getProviders({ page_size: 1000 }),
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

  const reopenMutation = useMutation({
    mutationFn: reopenPayroll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      queryClient.invalidateQueries({ queryKey: ['payroll-detail'] })
      enqueueSnackbar('Folha reaberta com sucesso!', { variant: 'success' })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number
      data: Partial<PayrollCreateData>
    }) => updatePayroll(id, data),
    onSuccess: (updatedData) => {
      // Update payrolls list cache manually for immediate feedback
      queryClient.setQueryData(
        ['payrolls', filters, page, rowsPerPage],
        (old: PaginatedResponse<Payroll>) => {
          if (!old) return old
          return {
            ...old,
            results: old.results.map((p: Payroll) =>
              p.id === updatedData.id ? { ...p, ...updatedData } : p
            ),
          }
        }
      )

      // Invalidate both queries to ensure total sync with backend
      queryClient.invalidateQueries({ queryKey: ['payrolls'] })
      queryClient.invalidateQueries({ queryKey: ['payroll-detail'] })

      setEditingPayroll(null)
      setOpenForm(false)
      enqueueSnackbar('Folha atualizada com sucesso!', { variant: 'success' })
    },
    onError: (error: Error) => {
      enqueueSnackbar(error.message, { variant: 'error' })
    },
  })

  const handleFormSubmit = (data: PayrollCreateData) => {
    if (editingPayroll) {
      updateMutation.mutate({ id: editingPayroll.id, data })
    } else {
      createMutation.mutate(data)
    }
  }

  const handleEdit = (payroll: PayrollDetail) => {
    setEditingPayroll(payroll)
    setOpenDetail(false)
    setOpenForm(true)
  }

  const handlePageChange = (newPage: number) => {
    setPage(newPage)
  }

  const handleRowsPerPageChange = (newRowsPerPage: number) => {
    setRowsPerPage(newRowsPerPage)
    setPage(0)
  }

  const handleViewDetails = (payroll: Payroll) => {
    setSelectedPayroll(payroll.id)
    setOpenDetail(true)
  }

  const handleDownloadFile = async (id: number) => {
    try {
      await downloadPayrollFile(id)
      enqueueSnackbar('Arquivo baixado com sucesso!', { variant: 'success' })
    } catch (error) {
      console.error(error)
      enqueueSnackbar('Erro ao baixar arquivo', { variant: 'error' })
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
      <PayrollStats />

      {/* Filters */}
      <PayrollFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        providers={providersData?.results}
      />

      {/* Table */}
      <GenericTable<Payroll>
        data={payrollsData?.results}
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
        totalCount={payrollsData?.count}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={handlePageChange}
        onRowsPerPageChange={handleRowsPerPageChange}
      />

      {/* Form Dialog */}
      <PayrollFormDialog
        open={openForm}
        onClose={() => {
          setOpenForm(false)
          setEditingPayroll(null)
        }}
        onSubmit={handleFormSubmit}
        providers={providersData?.results}
        isPending={createMutation.isPending || updateMutation.isPending}
        editingPayroll={editingPayroll}
      />

      {/* Detail Dialog */}
      <PayrollDetailDialog
        open={openDetail}
        onClose={() => setOpenDetail(false)}
        payrollDetail={payrollDetail}
        onEdit={handleEdit}
        onClosePayroll={(id) => closeMutation.mutate(id)}
        onMarkPaid={(id) => markPaidMutation.mutate(id)}
        onReopen={(id) => reopenMutation.mutate(id)}
        onDownloadFile={handleDownloadFile}
        isClosing={closeMutation.isPending}
        isMarkingPaid={markPaidMutation.isPending}
        isReopening={reopenMutation.isPending}
      />
    </Container>
  )
}

export default Payrolls
