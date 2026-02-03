import { useState } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Avatar,
  Divider,
  Chip,
  Menu,
  MenuItem,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Receipt as ReceiptIcon,
  Logout as LogoutIcon,
  Brightness4 as MoonIcon,
  Brightness7 as SunIcon,
  Business as BusinessIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { useThemeContext } from '../contexts/ThemeContext'
import { useAuth } from '../contexts/AuthContext'

const DRAWER_WIDTH = 260
const VIEW_PORT_WIDTH = 95

const MainLayout = () => {
  const { toggleTheme, mode } = useThemeContext()
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(true)
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Colaboradores', icon: <PeopleIcon />, path: '/admin/providers' },
    { text: 'Pagamentos', icon: <ReceiptIcon />, path: '/admin/payrolls' },
    { text: 'Configurações', icon: <SettingsIcon />, path: '/admin/settings' },
  ]

  const handleLogout = async () => {
    await logout()
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'SUPER_ADMIN':
        return 'error'
      case 'CUSTOMER_ADMIN':
        return 'primary'
      case 'PROVIDER':
        return 'success'
      default:
        return 'default'
    }
  }

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <List sx={{ px: 1, py: 10, flexGrow: 1, borderBottom: 1 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.text}
            selected={location.pathname === item.path}
            onClick={() => navigate(item.path)}
            sx={{
              minHeight: 48,
              borderRadius: 1,
              mb: 0.5,
              '&.Mui-selected': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          bgcolor: 'background.paper',
          color: 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle drawer"
            edge="start"
            onClick={() => setOpen(!open)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Box sx={{ flexGrow: 1 }} />

          <IconButton onClick={toggleTheme} color="inherit" sx={{ mr: 2 }}>
            {mode === 'dark' ? <SunIcon /> : <MoonIcon />}
          </IconButton>

          {/* User Info Menu */}
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                onClick={(e) => setAnchorEl(e.currentTarget)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  cursor: 'pointer',
                  p: 0.5,
                  borderRadius: 1,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <Box
                  sx={{
                    textAlign: 'right',
                    display: { xs: 'none', md: 'block' },
                  }}
                >
                  <Typography variant="subtitle2" fontWeight={600}>
                    {user.first_name || user.username}
                  </Typography>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5,
                      justifyContent: 'flex-end',
                    }}
                  >
                    {user.company_name && (
                      <>
                        <BusinessIcon sx={{ fontSize: 14 }} />
                        <Typography variant="caption" color="text.secondary">
                          {user.company_name}
                        </Typography>
                      </>
                    )}
                  </Box>
                </Box>
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: 0.5,
                  }}
                >
                  <Avatar
                    sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}
                  >
                    {(user.first_name || user.username)[0].toUpperCase()}
                  </Avatar>
                  <Chip
                    label={user.role_display}
                    size="small"
                    color={getRoleColor(user.role)}
                    sx={{ height: 18, fontSize: '0.65rem' }}
                  />
                </Box>
              </Box>

              <Menu
                anchorEl={anchorEl} // Uses the new state
                id="account-menu"
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
                onClick={() => setAnchorEl(null)}
                slotProps={{
                  paper: {
                    elevation: 0,
                    sx: {
                      overflow: 'visible',
                      filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
                      mt: 1.5,
                      minWidth: 200,
                      '&:before': {
                        content: '""',
                        display: 'block',
                        position: 'absolute',
                        top: 0,
                        right: 14,
                        width: 10,
                        height: 10,
                        bgcolor: 'background.paper',
                        transform: 'translateY(-50%) rotate(45deg)',
                        zIndex: 0,
                      },
                    },
                  },
                }}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <Box sx={{ px: 2, py: 1.5 }}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {user.first_name} {user.last_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {user.email}
                  </Typography>
                </Box>
                <Divider />
                {user.company_name && (
                  <MenuItem sx={{ py: 1.5 }}>
                    <ListItemIcon>
                      <BusinessIcon fontSize="small" />
                    </ListItemIcon>
                    <Box>
                      <Typography variant="body2" fontWeight={500}>
                        {user.company_name}
                      </Typography>
                      {user.company_cnpj && (
                        <Typography variant="caption" color="text.secondary">
                          CNPJ: {user.company_cnpj}
                        </Typography>
                      )}
                    </Box>
                  </MenuItem>
                )}
                <Divider />
                <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" color="error" />
                  </ListItemIcon>
                  Sair
                </MenuItem>
              </Menu>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Drawer
        variant="persistent"
        open={open}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        {drawerContent}
      </Drawer>

      <Box
        component="main"
        sx={(theme) => ({
          flexGrow: 1,
          p: 3,
          minHeight: '100vh',
          minWidth: open
            ? `calc(${VIEW_PORT_WIDTH}vw - ${DRAWER_WIDTH}px)`
            : `${VIEW_PORT_WIDTH}vw`,
          bgcolor: 'background.default',

          marginLeft: open ? 0 : `${-DRAWER_WIDTH}px`,

          transition: theme.transitions.create('margin', {
            easing: open
              ? theme.transitions.easing.easeOut
              : theme.transitions.easing.sharp,
            duration: open
              ? theme.transitions.duration.enteringScreen
              : theme.transitions.duration.leavingScreen,
          }),
        })}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Outlet />
      </Box>
    </Box>
  )
}

export default MainLayout
