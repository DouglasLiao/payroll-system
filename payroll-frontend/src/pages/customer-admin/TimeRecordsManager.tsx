import { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Grid,
} from '@mui/material'
import { Check, Close } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { useSnackbar } from 'notistack'
import dayjs from 'dayjs'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default function TimeRecordsManager() {
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()
  const [selectedAdjustment, setSelectedAdjustment] = useState<any>(null)

  const { data: adjustments, isLoading } = useQuery({
    queryKey: ['admin-time-adjustments'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/time-adjustments/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      // Filtrar apenas os PENDING? Ou mostrar todos?
      return response.data.results || response.data
    }
  })

  const { data: records } = useQuery({
    queryKey: ['admin-time-records'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/time-records/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      })
      return response.data.results || response.data
    }
  })

  const resolveMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string | number, status: 'APPROVED' | 'REJECTED' }) => {
      const response = await axios.patch(`${API_URL}/time-adjustments/${id}/`,
        { status },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      )
      return response.data
    },
    onSuccess: () => {
      enqueueSnackbar('Ajuste resolvido com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['admin-time-adjustments'] })
      queryClient.invalidateQueries({ queryKey: ['admin-time-records'] })
      setSelectedAdjustment(null)
    },
    onError: () => {
      enqueueSnackbar('Erro ao resolver ajuste.', { variant: 'error' })
    }
  })

  if (isLoading) return <Typography>Carregando...</Typography>

  const pendingAdjustments = (adjustments || []).filter((a: any) => a.status === 'PENDING')
  const historyAdjustments = (adjustments || []).filter((a: any) => a.status !== 'PENDING')

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Gestão de Ponto
      </Typography>

      <Grid container spacing={4}>
        <Grid size={{ xs: 12 }}>
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                Ajustes Pendentes de Aprovação ({pendingAdjustments.length})
              </Typography>
              {pendingAdjustments.length === 0 ? (
                <Typography color="text.secondary">Nenhum ajuste pendente.</Typography>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Colaborador</TableCell>
                        <TableCell>Data Afetada</TableCell>
                        <TableCell>Tipo</TableCell>
                        <TableCell>Novo Horário</TableCell>
                        <TableCell>Motivo</TableCell>
                        <TableCell align="center">Ações</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {pendingAdjustments.map((adj: any) => (
                        <TableRow key={adj.id}>
                          <TableCell>{adj.provider_name || 'Desconhecido'}</TableCell>
                          <TableCell>{dayjs(adj.target_date).format('DD/MM/YYYY')}</TableCell>
                          <TableCell>
                            <Chip
                              label={adj.adjustment_type === 'ENTRY' ? 'Entrada' : 'Saída'}
                              size="small"
                              color={adj.adjustment_type === 'ENTRY' ? 'info' : 'warning'}
                            />
                          </TableCell>
                          <TableCell>{adj.proposed_time.substring(0, 5)}</TableCell>
                          <TableCell>{adj.reason}</TableCell>
                          <TableCell align="center">
                            <IconButton
                              color="success"
                              onClick={() => resolveMutation.mutate({ id: adj.id, status: 'APPROVED' })}
                            >
                              <Check />
                            </IconButton>
                            <IconButton
                              color="error"
                              onClick={() => resolveMutation.mutate({ id: adj.id, status: 'REJECTED' })}
                            >
                              <Close />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                Registros de Ponto Recentes
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Colaborador</TableCell>
                      <TableCell>Data/Hora</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Localização</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(records || []).slice(0, 10).map((rec: any) => (
                      <TableRow key={rec.id}>
                        <TableCell>{rec.provider_name || 'Desconhecido'}</TableCell>
                        <TableCell>{dayjs(rec.timestamp).format('DD/MM/YYYY HH:mm')}</TableCell>
                        <TableCell>
                          <Chip
                            label={rec.record_type === 'ENTRY' ? 'Entrada' : 'Saída'}
                            size="small"
                            color={rec.record_type === 'ENTRY' ? 'info' : 'warning'}
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          {rec.latitude && rec.longitude
                            ? `${rec.latitude.substring(0, 8)}, ${rec.longitude.substring(0, 8)}`
                            : 'N/A'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
