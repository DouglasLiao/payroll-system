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
  Fade,
} from '@mui/material'
import { Link } from 'react-router-dom'
import { authApi } from '../services/authApi'
import { useMutation } from '@tanstack/react-query'

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('')
  const [success, setSuccess] = useState(false)

  const resetMutation = useMutation({
    mutationFn: (email: string) => authApi.requestPasswordReset(email),
    onSuccess: () => {
      setSuccess(true)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    resetMutation.mutate(email)
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
              Recuperar Senha
            </Typography>

            {success ? (
              <Box sx={{ width: '100%', textAlign: 'center' }}>
                <Alert severity="success" sx={{ mb: 3, mt: 2 }}>
                  Se o email estiver cadastrado, enviamos as instruções para
                  você.
                </Alert>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  Verifique sua caixa de entrada (e spam).
                </Typography>
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
                  Voltar para Login
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
                  Digite seu email abaixo e enviaremos um link seguro para você
                  redefinir sua senha.
                </Typography>

                {resetMutation.isError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    Ocorreu um erro ao processar sua solicitação. Tente
                    novamente.
                  </Alert>
                )}

                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Endereço de Email"
                  name="email"
                  autoComplete="email"
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
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
                    ? 'Enviando...'
                    : 'Enviar Link de Recuperação'}
                </Button>

                <Box sx={{ textAlign: 'center', mt: 3 }}>
                  <MuiLink
                    component={Link}
                    to="/login"
                    variant="body2"
                    sx={{
                      color: '#667eea',
                      textDecoration: 'none',
                      fontWeight: 600,
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    }}
                  >
                    Voltar para Login
                  </MuiLink>
                </Box>
              </Box>
            )}
          </Card>
        </Fade>
      </Container>
    </Box>
  )
}

export default ForgotPasswordPage
