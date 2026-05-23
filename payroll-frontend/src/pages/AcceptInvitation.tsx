import { useState, useEffect, type FormEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios, { isAxiosError } from 'axios'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Fade,
  useTheme,
  alpha,
  Divider,
  Chip,
} from '@mui/material'
import { Visibility, VisibilityOff, Lock, Person, Home, AccountBalance, Business } from '@mui/icons-material'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export default function AcceptInvitation() {
  const { uidb64, token } = useParams<{ uidb64: string; token: string }>()
  const navigate = useNavigate()
  const theme = useTheme()

  // Pre-filled read-only data from server
  const [providerName, setProviderName] = useState('')
  const [providerEmail, setProviderEmail] = useState('')
  const [providerRole, setProviderRole] = useState('')
  const [providerCompany, setProviderCompany] = useState('')

  // Editable fields
  const [address, setAddress] = useState('')
  const [pixKey, setPixKey] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [linkInvalid, setLinkInvalid] = useState(false)

  // Load provider data on mount
  useEffect(() => {
    const loadProviderData = async () => {
      try {
        const response = await axios.get(`${API_URL}/accept-invite/`, {
          params: { uidb64, token }
        })
        setProviderName(response.data.name || '')
        setProviderEmail(response.data.email || '')
        setProviderRole(response.data.role || '')
        setProviderCompany(response.data.company || '')
      } catch (err) {
        setLinkInvalid(true)
        setError(
          isAxiosError(err) && err.response?.data?.error
            ? err.response.data.error
            : 'Link de convite inválido ou expirado.'
        )
      } finally {
        setLoading(false)
      }
    }

    if (uidb64 && token) {
      loadProviderData()
    } else {
      setLinkInvalid(true)
      setLoading(false)
    }
  }, [uidb64, token])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.')
      return
    }
    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres.')
      return
    }

    setSubmitting(true)
    try {
      const response = await axios.post(`${API_URL}/accept-invite/`, {
        uidb64,
        token,
        password,
        name: providerName,
        address,
        pix_key: pixKey,
      })
      setSuccess(response.data.message || 'Cadastro concluído! Redirecionando para o login...')
      setTimeout(() => navigate('/login'), 3000)
    } catch (err: unknown) {
      setError(
        isAxiosError(err) && err.response?.data?.error
          ? err.response.data.error
          : 'Erro ao processar o convite.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  const inputStyle = {
    mb: 2,
    '& .MuiOutlinedInput-root': {
      backgroundColor: alpha(theme.palette.background.paper, 0.95),
    },
  }

  if (loading) {
    return (
      <Box sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundImage: 'url(/office-team.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        position: 'relative',
        py: 4,
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: 0,
          backgroundColor: alpha(theme.palette.common.black, 0.55),
          zIndex: 1,
        },
      }}
    >
      <Fade in timeout={700}>
        <Card
          sx={{
            maxWidth: 560,
            width: '92%',
            position: 'relative',
            zIndex: 2,
            backgroundColor: alpha(theme.palette.background.paper, 0.97),
            backdropFilter: 'blur(12px)',
            boxShadow: `0 12px 40px ${alpha(theme.palette.common.black, 0.35)}`,
            borderRadius: 3,
          }}
        >
          <CardContent sx={{ p: { xs: 3, md: 5 } }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Typography variant="h5" fontWeight="bold" gutterBottom color="primary">
                Bem-vindo ao Portal!
              </Typography>
              {providerCompany && (
                <Chip
                  icon={<Business fontSize="small" />}
                  label={providerCompany}
                  color="primary"
                  variant="outlined"
                  size="small"
                  sx={{ mb: 1 }}
                />
              )}
              <Typography variant="body2" color="text.secondary">
                Confirme seus dados e crie uma senha de acesso para concluir o cadastro.
              </Typography>
            </Box>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

            {!linkInvalid && (
              <form onSubmit={handleSubmit}>
                {/* Read-only info section */}
                <Typography variant="caption" color="text.secondary" fontWeight={600} gutterBottom>
                  DADOS DO CONTRATO (não editáveis)
                </Typography>
                <Box sx={{ mb: 2, p: 2, borderRadius: 2, bgcolor: alpha(theme.palette.action.selected, 0.5) }}>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 0.5 }}>
                    <Person fontSize="small" color="action" />
                    <Typography variant="body2" fontWeight={600}>{providerName || '(não informado)'}</Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ pl: 3.5 }}>
                    {providerRole} · {providerEmail}
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />
                <Typography variant="caption" color="text.secondary" fontWeight={600} gutterBottom>
                  SEUS DADOS PESSOAIS
                </Typography>

                <TextField
                  fullWidth
                  label="Endereço Completo *"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  required
                  multiline
                  rows={2}
                  sx={{ ...inputStyle, mt: 1 }}
                  placeholder="Ex: Rua das Flores, 123 – Bairro, Cidade/UF"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start" sx={{ alignSelf: 'flex-start', mt: 1.5 }}>
                        <Home sx={{ color: theme.palette.text.secondary }} />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  label="Chave PIX (opcional)"
                  value={pixKey}
                  onChange={(e) => setPixKey(e.target.value)}
                  sx={inputStyle}
                  placeholder="CPF, e-mail, telefone ou chave aleatória"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <AccountBalance sx={{ color: theme.palette.text.secondary }} />
                      </InputAdornment>
                    ),
                  }}
                />

                <Divider sx={{ my: 2 }} />
                <Typography variant="caption" color="text.secondary" fontWeight={600} gutterBottom>
                  CRIE SUA SENHA DE ACESSO
                </Typography>

                <TextField
                  fullWidth
                  label="Nova Senha *"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  sx={{ ...inputStyle, mt: 1 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: theme.palette.text.secondary }} />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  label="Confirmar Senha *"
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  sx={inputStyle}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: theme.palette.text.secondary }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={submitting || !!success}
                  sx={{ mt: 2, py: 1.5, fontWeight: 600, borderRadius: 2 }}
                >
                  {submitting ? <CircularProgress size={24} color="inherit" /> : 'Finalizar Cadastro'}
                </Button>
              </form>
            )}
          </CardContent>
        </Card>
      </Fade>
    </Box>
  )
}
