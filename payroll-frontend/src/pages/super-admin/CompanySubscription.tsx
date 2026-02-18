import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  FormControl,
  InputLabel,
  Select,
  TextField,
  Chip,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import {
  getSubscription,
  renewSubscription,
  getCompany,
} from '../../services/superAdminApi'
import { CustomMenuItem } from '../../components/CustomMenuItem'

const CompanySubscription = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()
  const companyId = Number(id)

  const [formData, setFormData] = useState({
    plan_type: 'BASIC',
    end_date: '',
  })

  // Fetch Company Info
  const { data: company, isLoading: isLoadingCompany } = useQuery({
    queryKey: ['company', companyId],
    queryFn: () => getCompany(companyId),
    enabled: !!companyId,
  })

  // Fetch Subscription
  const { data: subscription, isLoading: isLoadingSub } = useQuery({
    queryKey: ['subscription', companyId],
    queryFn: () => getSubscription(companyId),
    enabled: !!companyId,
  })

  // Update local state when sub loads
  useEffect(() => {
    if (subscription) {
      // eslint-disable-next-line
      setFormData((prev) => {
        if (
          prev.plan_type === subscription.plan_type &&
          prev.end_date === (subscription.end_date || '')
        ) {
          return prev
        }
        return {
          plan_type: subscription.plan_type,
          end_date: subscription.end_date || '',
        }
      })
    }
  }, [subscription])

  // Renew/Update Mutation
  const renewMutation = useMutation({
    mutationFn: (data: { plan_type: string; end_date: string }) =>
      renewSubscription(
        subscription!.id,
        data.plan_type,
        data.end_date || undefined
      ),
    onSuccess: () => {
      enqueueSnackbar('Assinatura atualizada com sucesso!', {
        variant: 'success',
      })
      queryClient.invalidateQueries({ queryKey: ['subscription', companyId] })
    },
    onError: () => {
      enqueueSnackbar('Erro ao atualizar assinatura.', { variant: 'error' })
    },
  })

  const handleSave = () => {
    if (!subscription) {
      enqueueSnackbar('Assinatura inexistente. Feature de criação pendente.', {
        variant: 'warning',
      })
      return
    }
    renewMutation.mutate(formData)
  }

  if (isLoadingCompany || isLoadingSub) {
    return (
      <Box sx={{ p: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (!company) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography color="error">Empresa não encontrada.</Typography>
      </Box>
    )
  }

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/super-admin/companies')}
        >
          Voltar
        </Button>
        <Typography variant="h4" fontWeight="bold">
          Assinatura de: {company.name}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Status Atual
              </Typography>

              {!subscription ? (
                <Alert severity="warning">
                  Nenhuma assinatura ativa encontrada.
                </Alert>
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                    mt: 2,
                  }}
                >
                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography color="textSecondary">Plano:</Typography>
                    <Chip
                      label={subscription.plan_type_display}
                      color="primary"
                    />
                  </Box>
                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography color="textSecondary">Status:</Typography>
                    <Chip
                      label={subscription.status_display}
                      color={subscription.is_active ? 'success' : 'error'}
                      icon={
                        subscription.is_active ? <CheckCircleIcon /> : undefined
                      }
                    />
                  </Box>
                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography color="textSecondary">Prestadores:</Typography>
                    <Typography fontWeight="bold">
                      {subscription.max_providers === null
                        ? 'Ilimitado'
                        : subscription.max_providers}
                    </Typography>
                  </Box>
                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography color="textSecondary">Vencimento:</Typography>
                    <Typography fontWeight="bold">
                      {subscription.end_date
                        ? new Date(subscription.end_date).toLocaleDateString(
                            'pt-BR'
                          )
                        : 'Vitalício'}
                    </Typography>
                  </Box>
                  <Box
                    sx={{ display: 'flex', justifyContent: 'space-between' }}
                  >
                    <Typography color="textSecondary">Valor Mensal:</Typography>
                    <Typography fontWeight="bold" color="success.main">
                      {new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL',
                      }).format(Number(subscription.price))}
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Gerenciar Assinatura
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Atualize o plano ou renove a assinatura.
            </Typography>

            <Grid container spacing={3}>
              <Grid size={{ xs: 12 }}>
                <FormControl fullWidth>
                  <InputLabel>Plano</InputLabel>
                  <Select
                    value={formData.plan_type}
                    label="Plano"
                    onChange={(e) =>
                      setFormData({ ...formData, plan_type: e.target.value })
                    }
                  >
                    <CustomMenuItem value="BASIC">
                      Basic (Até 5 prestadores)
                    </CustomMenuItem>
                    <CustomMenuItem value="PRO">
                      Pro (Até 20 prestadores)
                    </CustomMenuItem>
                    <CustomMenuItem value="ENTERPRISE">
                      Enterprise (Até 50 prestadores)
                    </CustomMenuItem>
                    <CustomMenuItem value="UNLIMITED">
                      Unlimited (Ilimitado)
                    </CustomMenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  label="Nova Data de Vencimento"
                  type="date"
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                  value={formData.end_date}
                  onChange={(e) =>
                    setFormData({ ...formData, end_date: e.target.value })
                  }
                  helperText="Deixe em branco para manter a atual ou definir como vitalício (se suportado)"
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  onClick={handleSave}
                  disabled={!subscription || renewMutation.isPending}
                >
                  Atualizar Assinatura
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default CompanySubscription
