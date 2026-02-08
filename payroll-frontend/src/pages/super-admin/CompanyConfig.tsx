import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Alert,
  Divider,
  CircularProgress,
} from '@mui/material'
import {
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import {
  getPayrollConfig,
  updatePayrollConfig,
  applyTemplateToCompany,
  getMathTemplates,
  getCompany,
} from '../../services/superAdminApi' // Verify if getCompany is exported
import type {
  PayrollMathTemplate,
  PayrollConfiguration,
  TransportVoucherType,
  BusinessDaysRule,
} from '../../types'

const CompanyConfig = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()
  const companyId = Number(id)

  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [formData, setFormData] = useState({
    overtime_percentage: '',
    night_shift_percentage: '',
    holiday_percentage: '',
    advance_percentage: '',
    transport_voucher_type: 'FIXED',
    business_days_rule: 'commercial',
  })

  // Fetch Company Info
  const { data: company, isLoading: isLoadingCompany } = useQuery({
    queryKey: ['company', companyId],
    queryFn: () => getCompany(companyId),
    enabled: !!companyId,
  })

  // Fetch Config
  const { data: config, isLoading: isLoadingConfig } = useQuery({
    queryKey: ['payrollConfig', companyId],
    queryFn: () => getPayrollConfig(companyId),
    enabled: !!companyId,
  })

  // Fetch Templates
  const { data: templates = [] } = useQuery({
    queryKey: ['mathTemplates'],
    queryFn: getMathTemplates,
  })

  // Update local state when config loads
  useEffect(() => {
    if (config) {
      // eslint-disable-next-line
      setFormData({
        overtime_percentage: config.overtime_percentage,
        night_shift_percentage: config.night_shift_percentage,
        holiday_percentage: config.holiday_percentage,
        advance_percentage: config.advance_percentage,
        transport_voucher_type: config.transport_voucher_type,
        business_days_rule: config.business_days_rule,
      })
    }
  }, [config])

  // Update Mutation
  const updateMutation = useMutation({
    mutationFn: (data: Partial<PayrollConfiguration>) =>
      updatePayrollConfig(config!.id, data),
    onSuccess: () => {
      enqueueSnackbar('Configuração atualizada com sucesso!', {
        variant: 'success',
      })
      queryClient.invalidateQueries({ queryKey: ['payrollConfig', companyId] })
    },
    onError: () => {
      enqueueSnackbar('Erro ao atualizar configuração.', { variant: 'error' })
    },
  })

  // Apply Template Mutation
  const applyTemplateMutation = useMutation({
    mutationFn: (templateId: number) =>
      applyTemplateToCompany(companyId, templateId),
    onSuccess: () => {
      enqueueSnackbar('Template aplicado com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['payrollConfig', companyId] })
      setSelectedTemplate('')
    },
    onError: () => {
      enqueueSnackbar('Erro ao aplicar template.', { variant: 'error' })
    },
  })

  const handleSave = () => {
    if (!config) {
      enqueueSnackbar(
        'Configuração não encontrada para esta empresa (feature pending creation).',
        { variant: 'warning' }
      )
      return
    }
    updateMutation.mutate(formData)
  }

  const handleApplyTemplate = () => {
    if (selectedTemplate) {
      applyTemplateMutation.mutate(Number(selectedTemplate))
    }
  }

  if (isLoadingCompany || isLoadingConfig) {
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
          Configuração de Folha: {company.name}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Template Selection */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Aplicar Template
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                Selecione um template pré-definido para aplicar configurações
                padrão rapidamente.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <FormControl size="small" sx={{ minWidth: 200 }}>
                  <InputLabel>Template</InputLabel>
                  <Select
                    label="Template"
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                  >
                    {templates.map((t: PayrollMathTemplate) => (
                      <MenuItem key={t.id} value={t.id}>
                        {t.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Button
                  variant="contained"
                  onClick={handleApplyTemplate}
                  disabled={
                    !selectedTemplate || applyTemplateMutation.isPending
                  }
                >
                  Aplicar
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Manual Configuration */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Box
              sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}
            >
              <Typography variant="h6">Regras de Cálculo</Typography>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={updateMutation.isPending || !config}
              >
                Salvar Alterações
              </Button>
            </Box>

            {!config && (
              <Alert severity="warning" sx={{ mb: 3 }}>
                Esta empresa ainda não possui configuração inicializada. Aplique
                um template primeiro.
              </Alert>
            )}

            <Grid container spacing={3}>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  label="Percentual Hora Extra (%)"
                  type="number"
                  fullWidth
                  value={formData.overtime_percentage}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      overtime_percentage: e.target.value,
                    })
                  }
                  helperText="Ex: 50 para 50%"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  label="Percentual Hora Noturna (%)"
                  type="number"
                  fullWidth
                  value={formData.night_shift_percentage}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      night_shift_percentage: e.target.value,
                    })
                  }
                  helperText="Ex: 20 para 20%"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  label="Percentual de Feriado (%)"
                  type="number"
                  fullWidth
                  value={formData.holiday_percentage}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      holiday_percentage: e.target.value,
                    })
                  }
                  helperText="Ex: 100 para 100%"
                />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField
                  label="Percentual de Adiantamento (%)"
                  type="number"
                  fullWidth
                  value={formData.advance_percentage}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      advance_percentage: e.target.value,
                    })
                  }
                  helperText="Padrão para novos prestadores"
                />
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <Divider sx={{ my: 1 }} />
              </Grid>

              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Tipo de Vale Transporte</InputLabel>
                  <Select
                    value={formData.transport_voucher_type}
                    label="Tipo de Vale Transporte"
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        transport_voucher_type: e.target
                          .value as TransportVoucherType,
                      })
                    }
                  >
                    <MenuItem value="FIXED">Fixo (Valor Integrado)</MenuItem>
                    <MenuItem value="DYNAMIC">
                      Dinâmico (Calculado por dia)
                    </MenuItem>
                    <MenuItem value="NONE">Não Utiliza</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Regra de Dias Úteis</InputLabel>
                  <Select
                    value={formData.business_days_rule}
                    label="Regra de Dias Úteis"
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        business_days_rule: e.target.value as BusinessDaysRule,
                      })
                    }
                  >
                    <MenuItem value="commercial">
                      Comercial (30 dias fixo)
                    </MenuItem>
                    <MenuItem value="calendar">
                      Calendário (Dias reais do mês)
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default CompanyConfig
