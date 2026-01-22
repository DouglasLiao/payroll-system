import { Box, Typography, Button } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { Block } from '@mui/icons-material'

export default function UnauthorizedPage() {
  const navigate = useNavigate()

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
      }}
    >
      <Block sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
      <Typography variant="h4" gutterBottom>
        Acesso Negado
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Você não tem permissão para acessar esta página.
      </Typography>
      <Button variant="contained" onClick={() => navigate('/')}>
        Voltar para o Início
      </Button>
    </Box>
  )
}
