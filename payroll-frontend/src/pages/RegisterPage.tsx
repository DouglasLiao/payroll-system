import { useState } from 'react'
import {
  Box,
  Button,
  Card,
  Container,
  TextField,
  Typography,
  Alert,
  Link as MuiLink,
  CircularProgress,
  Fade,
} from '@mui/material'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../services/authApi'
import { useMutation } from '@tanstack/react-query'

const RegisterPage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    company_name: '',
    company_cnpj: '',
    company_phone: '',
  })
  const [emailAvailable, setEmailAvailable] = useState<boolean | null>(null)

  const checkEmailMutation = useMutation({
    mutationFn: (email: string) => authApi.checkEmail(email),
    onSuccess: (data) => {
      setEmailAvailable(data.available)
    },
  })

  const registerMutation = useMutation({
    mutationFn: (data: typeof formData) => authApi.register(data),
    onSuccess: () => {
      navigate('/login', {
        state: {
          message: 'Conta criada! Aguarde a aprovação do administrador.',
        },
      })
    },
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    // Check email availability on blur
    if (name === 'email' && value.includes('@')) {
      checkEmailMutation.mutate(value)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.password !== formData.password_confirm) {
      alert('As senhas não coincidem')
      return
    }
    registerMutation.mutate(formData)
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background:
            'radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
        },
      }}
    >
      <Container maxWidth="sm" sx={{ position: 'relative', zIndex: 1 }}>
        <Fade in timeout={800}>
          <Card
            sx={{
              p: 4,
              backdropFilter: 'blur(10px)',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              borderRadius: 3,
            }}
          >
            <Typography
              component="h1"
              variant="h4"
              sx={{ mb: 1, fontWeight: 700, textAlign: 'center' }}
            >
              Criar Conta
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 3, textAlign: 'center' }}
            >
              Preencha os dados abaixo para começar
            </Typography>

            {registerMutation.isError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {(registerMutation.error as Error)?.message ||
                  'Erro ao criar conta'}
              </Alert>
            )}

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ width: '100%' }}
            >
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                sx={{ mb: 2 }}
                error={emailAvailable === false}
                helperText={
                  emailAvailable === false
                    ? 'Este email já está cadastrado'
                    : emailAvailable === true
                      ? '✓ Email disponível'
                      : ''
                }
              />

              <Typography
                variant="subtitle2"
                sx={{ mb: 1, mt: 2, fontWeight: 'bold' }}
              >
                Dados da Empresa
              </Typography>

              <TextField
                fullWidth
                label="Nome da Empresa"
                name="company_name"
                value={formData.company_name}
                onChange={handleChange}
                required
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  fullWidth
                  label="CNPJ"
                  name="company_cnpj"
                  value={formData.company_cnpj}
                  onChange={handleChange}
                  required
                />
                <TextField
                  fullWidth
                  label="Telefone"
                  name="company_phone"
                  value={formData.company_phone}
                  onChange={handleChange}
                />
              </Box>

              <Typography
                variant="subtitle2"
                sx={{ mb: 1, mt: 2, fontWeight: 'bold' }}
              >
                Dados do Usuário Master
              </Typography>

              <TextField
                fullWidth
                label="Nome de usuário"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                sx={{ mb: 2 }}
              />

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <TextField
                  fullWidth
                  label="Nome"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
                <TextField
                  fullWidth
                  label="Sobrenome"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </Box>

              <TextField
                fullWidth
                label="Senha"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                sx={{ mb: 2 }}
                helperText="Mínimo 8 caracteres"
              />

              <TextField
                fullWidth
                label="Confirmar Senha"
                name="password_confirm"
                type="password"
                value={formData.password_confirm}
                onChange={handleChange}
                required
                sx={{ mb: 3 }}
              />

              <Button
                fullWidth
                type="submit"
                variant="contained"
                size="large"
                disabled={
                  registerMutation.isPending || emailAvailable === false
                }
                sx={{
                  py: 1.5,
                  textTransform: 'none',
                  fontSize: '1rem',
                  fontWeight: 600,
                  background:
                    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  '&:hover': {
                    background:
                      'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                  },
                }}
              >
                {registerMutation.isPending ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'Criar Conta'
                )}
              </Button>

              <Box sx={{ textAlign: 'center', mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Já tem uma conta?{' '}
                  <MuiLink
                    component={Link}
                    to="/login"
                    sx={{ fontWeight: 600 }}
                  >
                    Fazer Login
                  </MuiLink>
                </Typography>
              </Box>
            </Box>
          </Card>
        </Fade>
      </Container>
    </Box>
  )
}

export default RegisterPage
