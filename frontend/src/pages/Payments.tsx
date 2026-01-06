import { Box, Typography, Button, Chip } from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import { Check, Download } from '@mui/icons-material'
import { getPayments, payPayment } from '../services/api'
import { GenericTable } from '../components/GenericTable'

const Payments = () => {
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()
  const { data: payments, isLoading } = useQuery({ queryKey: ['payments'], queryFn: getPayments })

  const payMutation = useMutation({
    mutationFn: payPayment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      enqueueSnackbar('Payment marked as PAID', { variant: 'success' })
    },
    onError: () => enqueueSnackbar('Error processing payment', { variant: 'error' }),
  })

  const handlePay = (id: number) => {
    if (confirm('Confirm payment?')) {
      payMutation.mutate(id)
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3, gap: 2 }}>
        <Typography variant="h4">Payments</Typography>
        <Button variant="outlined">Generate Monthly Roll</Button>
      </Box>

      <GenericTable
        data={payments}
        loading={isLoading}
        keyExtractor={(p) => p.id}
        columns={[
          { id: 'provider', label: 'Provider', accessor: 'provider_name' },
          { id: 'ref', label: 'Ref', accessor: 'reference' },
          {
            id: 'amount',
            label: 'Amount',
            render: (p) => `R$ ${p.total_calculated}`,
          },
          {
            id: 'status',
            label: 'Status',
            render: (p) => (
              <Chip
                label={p.status}
                color={p.status === 'PAID' ? 'success' : 'warning'}
                size="small"
              />
            ),
          },
          {
            id: 'actions',
            label: 'Actions',
            render: (p) => (
              <>
                {p.status === 'PENDING' && (
                  <Button size="small" startIcon={<Check />} onClick={() => handlePay(p.id)}>
                    Pay
                  </Button>
                )}
                {p.status === 'PAID' && (
                  <Button
                    size="small"
                    href={`http://localhost:8000/api/receipt/${p.id}/`}
                    target="_blank"
                    startIcon={<Download />}
                  >
                    Receipt
                  </Button>
                )}
              </>
            ),
          },
        ]}
      />
    </Box>
  )
}

export default Payments
