import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Grid,
  TextField,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Divider,
} from '@mui/material'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import dayjs, { Dayjs } from 'dayjs'
import 'dayjs/locale/pt-br'
import { downloadMonthlyReport, sendReportEmail } from 'src/services/api'
import { useSnackbar } from 'notistack'
import {
  Description as DescriptionIcon,
  Email as EmailIcon,
  Download as DownloadIcon,
} from '@mui/icons-material'

const Reports = () => {
  const [selectedDate, setSelectedDate] = useState<Dayjs | null>(dayjs())
  const [email, setEmail] = useState('')
  const [isDownloading, setIsDownloading] = useState(false)
  const [isSendingEmail, setIsSendingEmail] = useState(false)
  const { enqueueSnackbar } = useSnackbar()

  const handleDownload = async () => {
    if (!selectedDate) return

    try {
      const month = selectedDate.format('MM/YYYY')
      const currentMonth = dayjs()

      // Check if selected month is the current month or in the future
      if (
        selectedDate.isAfter(currentMonth, 'month') ||
        selectedDate.isSame(currentMonth, 'month')
      ) {
        enqueueSnackbar(
          'O mês selecionado ainda não terminou. Relatórios só podem ser gerados para meses encerrados.',
          { variant: 'warning' }
        )
        return
      }

      setIsDownloading(true)
      await downloadMonthlyReport(month)

      enqueueSnackbar('Relatório baixado com sucesso!', { variant: 'success' })
    } catch (error) {
      console.error(error)
      enqueueSnackbar('Erro ao baixar relatório.', { variant: 'error' })
    } finally {
      setIsDownloading(false)
    }
  }

  const handleSendEmail = async () => {
    if (!selectedDate) return

    try {
      setIsSendingEmail(true)
      const month = selectedDate.format('MM/YYYY')

      // Check if selected month is the current month or in the future
      if (
        selectedDate.isAfter(dayjs(), 'month') ||
        selectedDate.isSame(dayjs(), 'month')
      ) {
        enqueueSnackbar(
          'O mês selecionado ainda não terminou. Relatórios só podem ser gerados para meses encerrados.',
          { variant: 'warning' }
        )
        return
      }

      await sendReportEmail(month, email || undefined)

      enqueueSnackbar(`Relatório enviado para ${email || 'seu e-mail'}!`, {
        variant: 'success',
      })
      setEmail('')
    } catch (error) {
      console.error(error)
      enqueueSnackbar('Erro ao enviar e-mail.', { variant: 'error' })
    } finally {
      setIsSendingEmail(false)
    }
  }

  return (
    <Box sx={{ maxWidth: '100%', width: '100%', mt: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 'bold', color: 'primary.main' }}
        >
          Relatórios Mensais
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Gere e exporte relatórios consolidados da folha de pagamento.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Selection Card */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card
            elevation={0}
            sx={{ border: '1px solid', borderColor: 'divider', height: '100%' }}
          >
            <CardHeader
              title="Selecione o Período"
              subheader="Escolha o mês e ano de referência"
              avatar={<DescriptionIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <LocalizationProvider
                dateAdapter={AdapterDayjs}
                adapterLocale="pt-br"
              >
                <DatePicker
                  label="Mês de Referência"
                  views={['month', 'year']}
                  format="MM/YYYY"
                  value={selectedDate}
                  onChange={(newValue) => setSelectedDate(newValue)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      helperText:
                        'O relatório incluirá todos os pagamentos do mês selecionado.',
                    },
                  }}
                />
              </LocalizationProvider>
            </CardContent>
          </Card>
        </Grid>

        {/* Actions Card */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card
            elevation={0}
            sx={{ border: '1px solid', borderColor: 'divider', height: '100%' }}
          >
            <CardHeader
              title="Ações Disponíveis"
              subheader="Escolha como deseja obter o relatório"
              avatar={<DownloadIcon color="primary" />}
            />
            <Divider />
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  startIcon={
                    isDownloading ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      <DownloadIcon />
                    )
                  }
                  onClick={handleDownload}
                  disabled={isDownloading || !selectedDate}
                  sx={{ height: 48 }}
                >
                  {isDownloading ? 'Gerando Relatório...' : 'Baixar Relatório'}
                </Button>

                <Divider>OU</Divider>

                <Box
                  sx={{
                    display: 'flex',
                    gap: 2,
                    alignItems: 'flex-start',
                    flexDirection: { xs: 'column', sm: 'row' },
                  }}
                >
                  <TextField
                    label="E-mail Alternativo (opcional)"
                    placeholder="exemplo@email.com"
                    fullWidth
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    size="medium"
                    InputProps={{
                      startAdornment: (
                        <EmailIcon color="action" sx={{ mr: 1 }} />
                      ),
                    }}
                  />
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={
                      isSendingEmail ? (
                        <CircularProgress size={20} />
                      ) : (
                        <EmailIcon />
                      )
                    }
                    onClick={handleSendEmail}
                    disabled={isSendingEmail || !selectedDate}
                    sx={{ height: 56, minWidth: 160, whiteSpace: 'nowrap' }}
                  >
                    {isSendingEmail ? 'Enviando...' : 'Enviar por E-mail'}
                  </Button>
                </Box>
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: 'block', mt: -2 }}
                >
                  Se o campo de e-mail estiver vazio, o relatório será enviado
                  para o seu e-mail de cadastro.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Reports
