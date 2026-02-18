import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material'
import {
  Business,
  People,
  Receipt,
  AttachMoney,
  Description,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { getSuperAdminStats } from 'src/services/superAdminApi'

const Overview = () => {
  const {
    data: stats,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['superAdminStats'],
    queryFn: getSuperAdminStats,
  })

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography color="error">Erro ao carregar estatísticas.</Typography>
      </Box>
    )
  }

  const statCards = [
    {
      title: 'Empresas',
      value: stats?.total_companies || 0,
      icon: <Business sx={{ fontSize: 40, color: 'primary.main' }} />,
      color: 'primary.light',
    },
    {
      title: 'Prestadores',
      value: stats?.total_providers || 0,
      icon: <People sx={{ fontSize: 40, color: 'info.main' }} />,
      color: 'info.light',
    },
    {
      title: 'Assinaturas Ativas',
      value: stats?.active_subscriptions || 0,
      icon: <Receipt sx={{ fontSize: 40, color: 'success.main' }} />,
      color: 'success.light',
    },
    {
      title: 'MRR (Previsto)',
      value: new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
      }).format(stats?.mrr || 0),
      icon: <AttachMoney sx={{ fontSize: 40, color: 'warning.main' }} />,
      color: 'warning.light',
    },
    {
      title: 'Aprovações Pendentes',
      value: stats?.pending_approvals || 0,
      icon: <Description sx={{ fontSize: 40, color: 'error.main' }} />,
      color: 'error.light',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
        Visão Geral - Super Admin
      </Typography>

      <Grid container spacing={3}>
        {statCards.map((card, index) => (
          <Grid size={{ xs: 12, md: 6 }} key={index}>
            <Card
              sx={{ height: '100%', position: 'relative', overflow: 'visible' }}
            >
              <CardContent>
                <Box
                  sx={{
                    position: 'absolute',
                    top: -20,
                    right: 20,
                    width: 60,
                    height: 60,
                    borderRadius: 3,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: 'background.paper',
                    boxShadow: 3,
                  }}
                >
                  {card.icon}
                </Box>
                <Typography
                  color="textSecondary"
                  gutterBottom
                  variant="overline"
                >
                  {card.title}
                </Typography>
                <Typography
                  variant="h4"
                  component="div"
                  sx={{ mt: 2, fontWeight: 'medium' }}
                >
                  {card.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default Overview
