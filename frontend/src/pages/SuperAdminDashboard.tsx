import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  TextField,
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
  Chip,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Business as BusinessIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
import api from '../services/authApi'

interface Company {
  id: number
  name: string
  cnpj: string
  email: string
  phone: string
  is_active: boolean
  admin_count: number
  provider_count: number
  created_at: string
}

export default function SuperAdminDashboard() {
  const [openCompanyDialog, setOpenCompanyDialog] = useState(false)
  const [openAdminDialog, setOpenAdminDialog] = useState(false)
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()

  // Company form state
  const [companyForm, setCompanyForm] = useState({
    name: '',
    cnpj: '',
    email: '',
    phone: '',
  })

  // Admin form state
  const [adminForm, setAdminForm] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
  })

  // Fetch companies
  const { data: companies = [], isLoading } = useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const response = await api.get<Company[]>('/companies/')
      return response.data
    },
  })

  // Create company mutation
  const createCompanyMutation = useMutation({
    mutationFn: async (data: typeof companyForm) => {
      return await api.post('/companies/', data)
    },
    onSuccess: () => {
      enqueueSnackbar('Empresa criada com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      setOpenCompanyDialog(false)
      setCompanyForm({ name: '', cnpj: '', email: '', phone: '' })
    },
    onError: () => {
      enqueueSnackbar('Erro ao criar empresa', { variant: 'error' })
    },
  })

  // Delete company mutation
  const deleteCompanyMutation = useMutation({
    mutationFn: async (id: number) => {
      return await api.delete(`/companies/${id}/`)
    },
    onSuccess: () => {
      enqueueSnackbar('Empresa deletada com sucesso!', { variant: 'success' })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
    },
    onError: () => {
      enqueueSnackbar('Erro ao deletar empresa', { variant: 'error' })
    },
  })

  // Create admin mutation
  const createAdminMutation = useMutation({
    mutationFn: async (data: typeof adminForm) => {
      return await api.post(
        `/companies/${selectedCompany?.id}/create-admin/`,
        data
      )
    },
    onSuccess: () => {
      enqueueSnackbar('Administrador criado com sucesso!', {
        variant: 'success',
      })
      queryClient.invalidateQueries({ queryKey: ['companies'] })
      setOpenAdminDialog(false)
      setAdminForm({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
      })
      setSelectedCompany(null)
    },
    onError: () => {
      enqueueSnackbar('Erro ao criar administrador', { variant: 'error' })
    },
  })

  const handleCreateCompany = () => {
    createCompanyMutation.mutate(companyForm)
  }

  const handleDeleteCompany = (id: number) => {
    if (confirm('Tem certeza que deseja deletar esta empresa?')) {
      deleteCompanyMutation.mutate(id)
    }
  }

  const handleCreateAdmin = () => {
    createAdminMutation.mutate(adminForm)
  }

  return (
    <Box>
      <Box
        sx={{
          mb: 3,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Typography variant="h4" fontWeight="bold">
          Gerenciamento de Empresas
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenCompanyDialog(true)}
        >
          Nova Empresa
        </Button>
      </Box>

      {/* Companies Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Empresa</TableCell>
              <TableCell>CNPJ</TableCell>
              <TableCell>Contato</TableCell>
              <TableCell align="center">Admins</TableCell>
              <TableCell align="center">Colaboradores</TableCell>
              <TableCell align="center">Status</TableCell>
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
            ) : companies.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Nenhuma empresa cadastrada
                </TableCell>
              </TableRow>
            ) : (
              companies.map((company) => (
                <TableRow key={company.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BusinessIcon color="primary" />
                      <Typography variant="body2" fontWeight={500}>
                        {company.name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{company.cnpj}</TableCell>
                  <TableCell>
                    <Box>
                      <Box
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                      >
                        <EmailIcon sx={{ fontSize: 14 }} />
                        <Typography variant="caption">
                          {company.email}
                        </Typography>
                      </Box>
                      {company.phone && (
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                          }}
                        >
                          <PhoneIcon sx={{ fontSize: 14 }} />
                          <Typography variant="caption">
                            {company.phone}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell align="center">{company.admin_count}</TableCell>
                  <TableCell align="center">{company.provider_count}</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={company.is_active ? 'Ativa' : 'Inativa'}
                      color={company.is_active ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      size="small"
                      onClick={() => {
                        setSelectedCompany(company)
                        setOpenAdminDialog(true)
                      }}
                      sx={{ mr: 1 }}
                    >
                      + Admin
                    </Button>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteCompany(company.id)}
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

      {/* Create Company Dialog */}
      <Dialog
        open={openCompanyDialog}
        onClose={() => setOpenCompanyDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Nova Empresa</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Nome da Empresa"
              value={companyForm.name}
              onChange={(e) =>
                setCompanyForm({ ...companyForm, name: e.target.value })
              }
              fullWidth
              required
            />
            <TextField
              label="CNPJ"
              value={companyForm.cnpj}
              onChange={(e) =>
                setCompanyForm({ ...companyForm, cnpj: e.target.value })
              }
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={companyForm.email}
              onChange={(e) =>
                setCompanyForm({ ...companyForm, email: e.target.value })
              }
              fullWidth
              required
            />
            <TextField
              label="Telefone"
              value={companyForm.phone}
              onChange={(e) =>
                setCompanyForm({ ...companyForm, phone: e.target.value })
              }
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCompanyDialog(false)}>Cancelar</Button>
          <Button onClick={handleCreateCompany} variant="contained">
            Criar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Admin Dialog */}
      <Dialog
        open={openAdminDialog}
        onClose={() => setOpenAdminDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Novo Administrador - {selectedCompany?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
            <TextField
              label="Username (email)"
              value={adminForm.username}
              onChange={(e) =>
                setAdminForm({ ...adminForm, username: e.target.value })
              }
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={adminForm.email}
              onChange={(e) =>
                setAdminForm({ ...adminForm, email: e.target.value })
              }
              fullWidth
              required
            />
            <TextField
              label="Senha"
              type="password"
              value={adminForm.password}
              onChange={(e) =>
                setAdminForm({ ...adminForm, password: e.target.value })
              }
              fullWidth
              required
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Nome"
                value={adminForm.first_name}
                onChange={(e) =>
                  setAdminForm({ ...adminForm, first_name: e.target.value })
                }
                fullWidth
              />
              <TextField
                label="Sobrenome"
                value={adminForm.last_name}
                onChange={(e) =>
                  setAdminForm({ ...adminForm, last_name: e.target.value })
                }
                fullWidth
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAdminDialog(false)}>Cancelar</Button>
          <Button onClick={handleCreateAdmin} variant="contained">
            Criar Administrador
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
