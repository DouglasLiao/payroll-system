import { useState } from 'react'
import {
  Box,
  Button,
  Card,
  Container,
  TextField,
  Typography,
  Alert,
  Fade,
} from '@mui/material'
import { Link, useSearchParams } from 'react-router-dom'
import { authApi } from '../services/authApi'
import { useMutation } from '@tanstack/react-query'

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [passwords, setPasswords] = useState({ new: '', confirm: '' })
  const [success, setSuccess] = useState(false)

  const resetMutation = useMutation({
    mutationFn: (data: typeof passwords) =>
      authApi.confirmPasswordReset(token || '', data.new, data.confirm),
    onSuccess: () => {
      setSuccess(true)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) return
    if (passwords.new !== passwords.confirm) {
      alert('As senhas não conferem')
      return
    }
    resetMutation.mutate(passwords)
  }

  if (!token) {
    return (
      <Box
        sx={{
          width: '100%',
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <Container maxWidth="sm">
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
              <Alert severity="error" sx={{ mb: 3 }}>
                Link inválido ou expirado. Verifique o email recebido ou
                solicite um novo link.
              </Alert>
              <Button
                component={Link}
                to="/login"
                fullWidth
                variant="contained"
                size="large"
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
                Voltar para Login
              </Button>
            </Card>
          </Fade>
        </Container>
      </Box>
    )
  }

  return (
    <Box
      sx={{
        width: '100%',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
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
              Nova Senha
            </Typography>

            {success ? (
              <Box sx={{ width: '100%', textAlign: 'center' }}>
                <Alert severity="success" sx={{ mb: 3, mt: 2 }}>
                  Sua senha foi redefinida com sucesso!
                </Alert>
                <Button
                  component={Link}
                  to="/login"
                  variant="contained"
                  fullWidth
                  size="large"
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
                  Acessar minha conta
                </Button>
              </Box>
            ) : (
              <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{ width: '100%', mt: 1 }}
              >
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3, textAlign: 'center' }}
                >
                  Crie uma senha forte com no mínimo 8 caracteres.
                </Typography>

                {resetMutation.isError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {/* @ts-ignore */}
                    {resetMutation.error?.response?.data?.message ||
                      // @ts-ignore
                      Object.values(
                        resetMutation.error?.response?.data || {}
                      )[0] ||
                      'Erro ao redefinir senha'}
                  </Alert>
                )}

                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Nova Senha"
                  type="password"
                  id="password"
                  value={passwords.new}
                  onChange={(e) =>
                    setPasswords({ ...passwords, new: e.target.value })
                  }
                  disabled={resetMutation.isPending}
                  sx={{
                    mb: 2,
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      '& fieldset': {
                        borderColor: 'rgba(0, 0, 0, 0.23)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(0, 0, 0, 0.5)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#667eea',
                      },
                    },
                  }}
                />

                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="confirmPassword"
                  label="Confirmar Nova Senha"
                  type="password"
                  id="confirmPassword"
                  value={passwords.confirm}
                  onChange={(e) =>
                    setPasswords({ ...passwords, confirm: e.target.value })
                  }
                  disabled={resetMutation.isPending}
                  sx={{
                    mb: 3,
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255, 255, 255, 0.9)',
                      '& fieldset': {
                        borderColor: 'rgba(0, 0, 0, 0.23)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(0, 0, 0, 0.5)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#667eea',
                      },
                    },
                  }}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={resetMutation.isPending}
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
                  {resetMutation.isPending
                    ? 'Salvando...'
                    : 'Definir Nova Senha'}
                </Button>
              </Box>
            )}
          </Card>
        </Fade>
      </Container>
    </Box>
  )
}

export default ResetPasswordPage
