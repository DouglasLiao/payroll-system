import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
} from '@mui/material'
import { CustomMenuItem } from 'src/components/menu'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import {
  getMathTemplates,
  createMathTemplate,
  updateMathTemplate,
  deleteMathTemplate,
} from 'src/services/superAdminApi'
import type {
  PayrollMathTemplate,
  TransportVoucherType,
  BusinessDaysRule,
} from 'src/types'

const MathTemplateManager = () => {
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedTemplate, setSelectedTemplate] =
    useState<PayrollMathTemplate | null>(null)
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    overtime_percentage: '',
    night_shift_percentage: '',
    holiday_percentage: '',
    advance_percentage: '',
    transport_voucher_type: 'FIXED' as TransportVoucherType,
    business_days_rule: 'FIXED_30' as BusinessDaysRule,
  })

  // Fetch Templates
  const { data: templates = [], isLoading } = useQuery({
    queryKey: ['mathTemplates'],
    queryFn: getMathTemplates,
  })

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      overtime_percentage: '',
      night_shift_percentage: '',
      holiday_percentage: '',
      advance_percentage: '',
      transport_voucher_type: 'FIXED',
      business_days_rule: 'FIXED_30',
    })
    setSelectedTemplate(null)
  }

  const handleOpenCreate = () => {
    resetForm()
    setOpenDialog(true)
  }

  const handleOpenEdit = (template: PayrollMathTemplate) => {
    setSelectedTemplate(template)
    setFormData({
      name: template.name,
      description: template.description || '',
      overtime_percentage: template.overtime_percentage,
      night_shift_percentage: template.night_shift_percentage,
      holiday_percentage: template.holiday_percentage,
      advance_percentage: template.advance_percentage,
      transport_voucher_type: template.transport_voucher_type,
      business_days_rule: template.business_days_rule,
    })
    setOpenDialog(true)
  }

  // Create Mutation
  const createMutation = useMutation({
    mutationFn: createMathTemplate,
    onSuccess: () => {
      enqueueSnackbar('Template criado com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['mathTemplates'] })
      setOpenDialog(false)
    },
    onError: () =>
      enqueueSnackbar('Erro ao criar template.', { variant: 'error' }),
  })

  // Update Mutation
  const updateMutation = useMutation({
    mutationFn: (data: Partial<PayrollMathTemplate>) =>
      updateMathTemplate(selectedTemplate!.id, data),
    onSuccess: () => {
      enqueueSnackbar('Template atualizado!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['mathTemplates'] })
      setOpenDialog(false)
    },
    onError: () =>
      enqueueSnackbar('Erro ao atualizar template.', { variant: 'error' }),
  })

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: deleteMathTemplate,
    onSuccess: () => {
      enqueueSnackbar('Template removido!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['mathTemplates'] })
    },
    onError: () =>
      enqueueSnackbar('Erro ao remover template.', { variant: 'error' }),
  })

  const handleSubmit = () => {
    if (selectedTemplate) {
      updateMutation.mutate(formData)
    } else {
      createMutation.mutate(formData)
    }
  }

  return (
    <Box>
      <Box
        sx={{
          mb: 4,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="h4" fontWeight="bold">
          Gerenciamento de Templates
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenCreate}
        >
          Novo Template
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Nome</TableCell>
              <TableCell>Extras (%)</TableCell>
              <TableCell>Feriado (%)</TableCell>
              <TableCell>Noturno (%)</TableCell>
              <TableCell>Adiant. (%)</TableCell>
              <TableCell>VT</TableCell>
              <TableCell align="right">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Carregando...
                </TableCell>
              </TableRow>
            ) : templates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Nenhum template encontrado.
                </TableCell>
              </TableRow>
            ) : (
              templates.map((t: PayrollMathTemplate) => (
                <TableRow key={t.id}>
                  <TableCell>
                    <Typography
                      variant="subtitle2"
                      sx={{ display: 'flex', alignItems: 'center' }}
                    >
                      {t.name}
                      {t.is_default && (
                        <Box
                          component="span"
                          sx={{
                            ml: 1,
                            px: 1,
                            py: 0.25,
                            bgcolor: 'primary.main',
                            color: 'primary.contrastText',
                            borderRadius: 1,
                            fontSize: '0.65rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                          }}
                        >
                          Padrão
                        </Box>
                      )}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {t.description}
                    </Typography>
                  </TableCell>
                  <TableCell>{t.overtime_percentage}%</TableCell>
                  <TableCell>{t.holiday_percentage}%</TableCell>
                  <TableCell>{t.night_shift_percentage}%</TableCell>
                  <TableCell>{t.advance_percentage}%</TableCell>
                  <TableCell>{t.transport_voucher_type}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenEdit(t)}
                      title={t.is_default ? 'Visualizar' : 'Editar'}
                    >
                      {t.is_default ? <VisibilityIcon /> : <EditIcon />}
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => {
                        if (confirm('Excluir este template?'))
                          deleteMutation.mutate(t.id)
                      }}
                      disabled={t.is_default}
                      title={
                        t.is_default
                          ? 'Template padrão não pode ser excluído'
                          : 'Excluir'
                      }
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTemplate?.is_default
            ? 'Visualizar Template Padrão'
            : selectedTemplate
              ? 'Editar Template'
              : 'Novo Template'}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ pt: 1 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                label="Nome do Template"
                fullWidth
                disabled={!!selectedTemplate?.is_default}
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <TextField
                label="Descrição"
                fullWidth
                multiline
                rows={2}
                disabled={!!selectedTemplate?.is_default}
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
              />
            </Grid>
            <Grid size={{ xs: 6 }}>
              <TextField
                label="Hora Extra (%)"
                type="number"
                fullWidth
                disabled={!!selectedTemplate?.is_default}
                value={formData.overtime_percentage}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    overtime_percentage: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid size={{ xs: 6 }}>
              <TextField
                label="Feriado (%)"
                type="number"
                fullWidth
                disabled={!!selectedTemplate?.is_default}
                value={formData.holiday_percentage}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    holiday_percentage: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid size={{ xs: 6 }}>
              <TextField
                label="Adicional Noturno (%)"
                type="number"
                fullWidth
                disabled={!!selectedTemplate?.is_default}
                value={formData.night_shift_percentage}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    night_shift_percentage: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid size={{ xs: 6 }}>
              <TextField
                label="Adiantamento Padrão (%)"
                type="number"
                fullWidth
                disabled={!!selectedTemplate?.is_default}
                value={formData.advance_percentage}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    advance_percentage: e.target.value,
                  })
                }
              />
            </Grid>
            <Grid size={{ xs: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Vale Transporte</InputLabel>
                <Select
                  value={formData.transport_voucher_type}
                  label="Tipo de Vale Transporte"
                  disabled={!!selectedTemplate?.is_default}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      transport_voucher_type: e.target
                        .value as TransportVoucherType,
                    })
                  }
                >
                  <CustomMenuItem value="FIXED">Fixo</CustomMenuItem>
                  <CustomMenuItem value="DYNAMIC_PER_DAY">
                    Dinâmico (por dia)
                  </CustomMenuItem>
                  <CustomMenuItem value="DYNAMIC_PER_TRIP">
                    Dinâmico (por viagem)
                  </CustomMenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 6 }}>
              <FormControl fullWidth>
                <InputLabel>Regra Dias Úteis</InputLabel>
                <Select
                  value={formData.business_days_rule}
                  label="Regra Dias Úteis"
                  disabled={!!selectedTemplate?.is_default}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      business_days_rule: e.target.value as BusinessDaysRule,
                    })
                  }
                >
                  <CustomMenuItem value="FIXED_30">
                    Comercial (30 dias)
                  </CustomMenuItem>
                  <CustomMenuItem value="WORKALENDAR">
                    Calendário Real
                  </CustomMenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>
            {selectedTemplate?.is_default ? 'Fechar' : 'Cancelar'}
          </Button>
          {!selectedTemplate?.is_default && (
            <Button variant="contained" onClick={handleSubmit}>
              Salvar
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default MathTemplateManager
