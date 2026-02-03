import { useState, useEffect, useRef } from 'react'
import {
  Box,
  Typography,
  Button,
  Card,
  Container,
  TextField,
  Grid,
  Alert,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material'
import {
  Save,
  Info as InfoIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import { useSnackbar } from 'notistack'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { getProviders, updateProvider } from '../services/api'
import type { Provider } from '../types'

const Settings = () => {
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()
  const [vtFare, setVtFare] = useState('4.60')
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false)
  const [affectedProviders, setAffectedProviders] = useState<Provider[]>([])
  const hasInitializedRef = useRef(false)

  // Fetch all providers to get current VT fare
  const { data: providersData, isLoading } = useQuery({
    queryKey: ['providers-all'],
    queryFn: () => getProviders({ page: 1, page_size: 1000 }),
  })

  // Set initial VT fare from first provider with VT enabled
  useEffect(() => {
    if (providersData?.results && !hasInitializedRef.current) {
      const firstWithVT = providersData.results.find((p) => p.vt_enabled)
      if (firstWithVT && firstWithVT.vt_fare) {
        // Use setTimeout to avoid synchronous setState warning during effect body
        setTimeout(() => {
          setVtFare(firstWithVT.vt_fare)
          hasInitializedRef.current = true
        }, 0)
      }
    }
  }, [providersData])

  const handleSaveClick = () => {
    if (!providersData?.results) return

    // Find all providers with VT enabled
    const affected = providersData.results.filter((p) => p.vt_enabled)
    setAffectedProviders(affected)
    setConfirmDialogOpen(true)
  }

  const handleConfirmUpdate = async () => {
    try {
      // Update all providers with VT enabled
      const updatePromises = affectedProviders.map((provider) =>
        updateProvider(provider.id, { vt_fare: vtFare })
      )

      await Promise.all(updatePromises)

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      queryClient.invalidateQueries({ queryKey: ['providers-all'] })

      enqueueSnackbar(
        `Tarifa atualizada para ${affectedProviders.length} colaborador(es)!`,
        { variant: 'success' }
      )
      setConfirmDialogOpen(false)
    } catch (error) {
      enqueueSnackbar(`Erro ao atualizar tarifa ${String(error)}`, {
        variant: 'error',
      })
    }
  }

  if (isLoading) {
    return (
      <Container
        maxWidth="lg"
        sx={{ py: 4, display: 'flex', justifyContent: 'center' }}
      >
        <CircularProgress />
      </Container>
    )
  }

  const providersWithVT =
    providersData?.results?.filter((p) => p.vt_enabled) || []

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        ⚙️ Configurações
      </Typography>

      {/* VT Configuration Section */}
      <Card sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="h6"
            sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
          >
            🚌 Vale Transporte
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure a tarifa do vale transporte para todos os colaboradores
          </Typography>
        </Box>

        <Alert severity="info" icon={<InfoIcon />} sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Atenção:</strong> Esta ação atualizará a tarifa de VT para
            TODOS os {providersWithVT.length} colaboradores que recebem Vale
            Transporte.
          </Typography>
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              label="Tarifa da Passagem (R$)"
              value={vtFare}
              onChange={(e) => setVtFare(e.target.value)}
              fullWidth
              placeholder="4.60"
              helperText={`Será aplicado a ${providersWithVT.length} colaborador(es) com VT`}
              type="number"
              inputProps={{ step: '0.01', min: '0' }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper
              sx={{
                p: 2,
                bgcolor: 'primary.50',
                border: '1px solid',
                borderColor: 'primary.200',
              }}
            >
              <Typography
                variant="caption"
                color="text.secondary"
                display="block"
              >
                Exemplo de cálculo mensal:
              </Typography>
              <Typography variant="h6" color="primary.main">
                4 viagens x R$ {vtFare} x 22 dias = R${' '}
                {(4 * parseFloat(vtFare || '0') * 22).toFixed(2)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                (2 ônibus, ida e volta, mês completo)
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSaveClick}
            disabled={providersWithVT.length === 0}
          >
            Atualizar Tarifa para Todos
          </Button>
        </Box>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialogOpen}
        onClose={() => setConfirmDialogOpen(false)}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WarningIcon color="warning" />
            Confirmar Atualização em Massa
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Você está prestes a atualizar a tarifa de VT para{' '}
            <strong>{affectedProviders.length} colaboradores</strong>.
          </Alert>
          <Typography variant="body2">
            Colaboradores que serão afetados:
          </Typography>
          <Box sx={{ mt: 1, maxHeight: 200, overflow: 'auto' }}>
            <ul>
              {affectedProviders.map((p) => (
                <li key={p.id}>
                  <Typography variant="body2">
                    {p.name} - Atual: R$ {p.vt_fare} → Novo: R$ {vtFare}
                  </Typography>
                </li>
              ))}
            </ul>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleConfirmUpdate}
            color="primary"
          >
            Confirmar Atualização
          </Button>
        </DialogActions>
      </Dialog>

      {/* Future Features Section */}
      <Card sx={{ p: 3, bgcolor: 'grey.50' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          🔮 Recursos Futuros
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Web Scraping Automático:</strong> Em desenvolvimento
          </Typography>
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Futuramente, o sistema buscará automaticamente o valor atualizado da
            tarifa diretamente dos sites oficiais de transporte público.
          </Typography>
        </Alert>

        <Typography variant="body2" color="text.secondary">
          Outras melhorias planejadas:
        </Typography>
        <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
          <li>
            <Typography variant="body2" color="text.secondary">
              Atualização automática de tarifas por região
            </Typography>
          </li>
          <li>
            <Typography variant="body2" color="text.secondary">
              Histórico de alterações de tarifas
            </Typography>
          </li>
          <li>
            <Typography variant="body2" color="text.secondary">
              Notificações quando houver mudança de tarifa
            </Typography>
          </li>
        </ul>
      </Card>
    </Container>
  )
}

export default Settings
