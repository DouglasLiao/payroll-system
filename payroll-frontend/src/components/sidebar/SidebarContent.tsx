import { useLocation, useNavigate } from 'react-router-dom'
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Avatar,
  useTheme,
  alpha,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Receipt as ReceiptIcon,
  Business as BusinessIcon,
  Settings as SettingsIcon,
  Description as DescriptionIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material'
import { useAuth } from 'src/contexts/AuthContext'

export function SidebarContent() {
  const theme = useTheme()
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const menuItems =
    user?.role === 'SUPER_ADMIN'
      ? [
          {
            text: 'Dashboard',
            icon: <DashboardIcon />,
            path: '/super-admin/dashboard',
          },
          {
            text: 'Empresas',
            icon: <BusinessIcon />,
            path: '/super-admin/companies',
          },
          {
            text: 'Aprovações',
            icon: <PeopleIcon />,
            path: '/super-admin/approvals',
          },
          {
            text: 'Assinaturas',
            icon: <DescriptionIcon />,
            path: '/super-admin/subscriptions',
          },
          {
            text: 'Configurações',
            icon: <SettingsIcon />,
            path: '/super-admin/configs',
          },
        ]
      : [
          { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
          {
            text: 'Colaboradores',
            icon: <PeopleIcon />,
            path: '/admin/providers',
          },
          {
            text: 'Pagamentos',
            icon: <ReceiptIcon />,
            path: '/admin/payrolls',
          },
          {
            text: 'Relatórios',
            icon: <DescriptionIcon />,
            path: '/admin/reports',
          },
          {
            text: 'Configurações',
            icon: <SettingsIcon />,
            path: '/admin/settings',
          },
        ]

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: theme.palette.background.paper,
        color: theme.palette.text.primary,
      }}
    >
      <Box
        sx={{
          px: 2.5,
          py: 2.5,
          gap: 1.5,
          minHeight: 64,
        }}
      ></Box>

      {/* Nav items */}
      <List sx={{ px: 1.5, py: 1.5, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path
          return (
            <ListItemButton
              key={item.text}
              selected={isSelected}
              onClick={() => navigate(item.path)}
              sx={{
                borderRadius: 1.5,
                mb: 0.5,
                color: isSelected
                  ? theme.palette.primary.main
                  : theme.palette.text.secondary,
                '&:hover': {
                  bgcolor: alpha(theme.palette.primary.main, 0.08),
                  color: theme.palette.primary.main,
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.main,
                  },
                },
                '&.Mui-selected': {
                  bgcolor: alpha(theme.palette.primary.main, 0.16),
                  color: theme.palette.primary.main,
                  '&:hover': {
                    bgcolor: alpha(theme.palette.primary.main, 0.24),
                  },
                  '& .MuiListItemIcon-root': {
                    color: theme.palette.primary.main,
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 38,
                  color: isSelected
                    ? theme.palette.primary.main
                    : theme.palette.text.secondary,
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                slotProps={{
                  primary: {
                    fontSize: '0.875rem',
                    fontWeight: isSelected ? 600 : 400,
                  },
                }}
              />
            </ListItemButton>
          )
        })}
      </List>

      <Divider sx={{ borderColor: theme.palette.divider }} />

      {/* User footer */}
      {user && (
        <Box sx={{ px: 2, py: 2 }}>
          <Box
            sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}
          >
            <Avatar
              sx={{
                width: 34,
                height: 34,
                bgcolor: theme.palette.primary.main,
                color: theme.palette.primary.contrastText,
                fontSize: '0.875rem',
              }}
            >
              {(user.first_name || user.username)[0].toUpperCase()}
            </Avatar>
            <Box sx={{ overflow: 'hidden' }}>
              <Typography
                variant="body2"
                fontWeight={600}
                sx={{
                  color: theme.palette.text.primary,
                  lineHeight: 1.2,
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {user.first_name || user.username}
              </Typography>
              {user.company_name && (
                <Typography
                  variant="caption"
                  sx={{
                    color: theme.palette.text.secondary,
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: 'block',
                  }}
                >
                  {user.company_name}
                </Typography>
              )}
            </Box>
          </Box>

          <ListItemButton
            onClick={logout}
            sx={{
              borderRadius: 1.5,
              color: theme.palette.text.secondary,
              px: 1,
              py: 0.75,
              '&:hover': {
                bgcolor: alpha(theme.palette.error.main, 0.1),
                color: theme.palette.error.main,
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 34, color: 'inherit' }}>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText
              primary="Sair"
              slotProps={{ primary: { fontSize: '0.85rem' } }}
            />
          </ListItemButton>
        </Box>
      )}
    </Box>
  )
}
