import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import { Check, Download } from '@mui/icons-material'
import { getPayments, payPayment } from '../services/api'

const Payments = () => {
  const queryClient = useQueryClient()
  const { enqueueSnackbar } = useSnackbar()
  const { data: payments } = useQuery({ queryKey: ['payments'], queryFn: getPayments })

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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Payments</Typography>
        <Button variant="outlined">Generate Monthly Roll</Button>
      </Box>

      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Provider</TableCell>
              <TableCell>Ref</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {payments?.map((payment) => (
              <TableRow key={payment.id}>
                <TableCell>{payment.provider_name}</TableCell>
                <TableCell>{payment.reference}</TableCell>
                <TableCell>R$ {payment.total_calculated}</TableCell>
                <TableCell>
                  <Chip
                    label={payment.status}
                    color={payment.status === 'PAID' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {payment.status === 'PENDING' && (
                    <Button
                      size="small"
                      startIcon={<Check />}
                      onClick={() => handlePay(payment.id)}
                    >
                      Pay
                    </Button>
                  )}
                  {payment.status === 'PAID' && (
                    <Button
                      size="small"
                      href={`http://localhost:8000/api/receipt/${payment.id}/`}
                      target="_blank"
                      startIcon={<Download />}
                    >
                      Receipt
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  )
}

export default Payments
