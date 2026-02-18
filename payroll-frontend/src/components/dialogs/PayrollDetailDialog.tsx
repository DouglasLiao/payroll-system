import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import {
  FileDownload,
  Lock,
  Payment,
  LockOpen,
  Edit,
} from '@mui/icons-material'
import type { PayrollDetail } from 'src/types'
import { formatCurrency } from 'src/utils/formatters'
import { StatusChip } from 'src/components/table/StatusChip'

interface PayrollDetailDialogProps {
  open: boolean
  onClose: () => void // Closes the dialog
  payrollDetail?: PayrollDetail
  onEdit: (payroll: PayrollDetail) => void // Opens edit form
  onClosePayroll: (id: number) => void // Closes the payroll (DRAFT → CLOSED)
  onMarkPaid: (id: number) => void
  onReopen: (id: number) => void
  onDownloadFile: (id: number) => void
  isClosing: boolean
  isMarkingPaid: boolean
  isReopening: boolean
}

export const PayrollDetailDialog = ({
  open,
  onClose,
  payrollDetail,
  onEdit,
  onClosePayroll,
  onMarkPaid,
  onReopen,
  onDownloadFile,
  isClosing,
  isMarkingPaid,
  isReopening,
}: PayrollDetailDialogProps) => {
  if (!payrollDetail) return null

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        {payrollDetail.provider.name} - {payrollDetail.reference_month}
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <StatusChip
                status={payrollDetail.status as 'DRAFT' | 'CLOSED' | 'PAID'}
                label={payrollDetail.status_display}
              />
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<FileDownload />}
                  onClick={() => onDownloadFile(payrollDetail.id)}
                >
                  Download da Folha
                </Button>

                {/* DRAFT status: Can edit or close payroll */}
                {payrollDetail.status === 'DRAFT' && (
                  <>
                    <Button
                      variant="outlined"
                      color="primary"
                      startIcon={<Edit />}
                      onClick={() => onEdit(payrollDetail)}
                    >
                      Editar
                    </Button>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<Lock />}
                      onClick={() => onClosePayroll(payrollDetail.id)}
                      disabled={isClosing}
                    >
                      Fechar Folha
                    </Button>
                  </>
                )}

                {/* CLOSED status: Can mark as paid or reopen */}
                {payrollDetail.status === 'CLOSED' && (
                  <>
                    <Button
                      variant="outlined"
                      color="warning"
                      startIcon={<LockOpen />}
                      onClick={() => onReopen(payrollDetail.id)}
                      disabled={isReopening}
                    >
                      Reabrir
                    </Button>
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={<Payment />}
                      onClick={() => onMarkPaid(payrollDetail.id)}
                      disabled={isMarkingPaid}
                    >
                      Marcar como Paga
                    </Button>
                  </>
                )}

                {/* PAID status: No actions allowed (final state) */}
              </Box>
            </Box>
          </Grid>

          <Grid size={{ xs: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="success.main">
                  💰 Proventos
                </Typography>
                <Box
                  sx={{
                    '& > div': {
                      display: 'flex',
                      justifyContent: 'space-between',
                    },
                  }}
                >
                  <div>
                    <Typography variant="body2">Saldo base:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.remaining_value)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">Horas extras:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.overtime_amount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">Feriados:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.holiday_amount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">DSR:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.dsr_amount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">Adicional noturno:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.night_shift_amount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="subtitle1" fontWeight={700}>
                      Total:
                    </Typography>
                    <Typography fontWeight={700} color="success.main">
                      {formatCurrency(payrollDetail.total_earnings)}
                    </Typography>
                  </div>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error.main">
                  Descontos
                </Typography>
                <Box
                  sx={{
                    '& > div': {
                      display: 'flex',
                      justifyContent: 'space-between',
                    },
                  }}
                >
                  <div>
                    <Typography variant="body2">Adiantamento:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.advance_value)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">Atrasos:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.late_discount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">Faltas:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.absence_discount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">DSR s/ faltas:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.dsr_on_absences)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="body2">Vale transporte:</Typography>
                    <Typography>
                      {formatCurrency(payrollDetail.vt_discount)}
                    </Typography>
                  </div>
                  <div>
                    <Typography variant="subtitle1" fontWeight={700}>
                      Total:
                    </Typography>
                    <Typography fontWeight={700} color="error.main">
                      {formatCurrency(payrollDetail.total_discounts)}
                    </Typography>
                  </div>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12 }}>
            <Card
              sx={{
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
              }}
            >
              <CardContent>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Typography variant="h5" color="inherit">
                    Valor Líquido
                  </Typography>
                  <Typography variant="h3" fontWeight={700} color="inherit">
                    {formatCurrency(payrollDetail.net_value)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  )
}
