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
  useTheme,
  useMediaQuery,
  styled,
  type CSSObject,
  type Theme,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Payment as PaymentIcon,
  Logout as LogoutIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Brightness4 as MoonIcon,
  Brightness7 as SunIcon,
} from '@mui/icons-material'
import { useThemeContext } from '../contexts/ThemeContext'

const DRAWER_WIDTH = 260
const CLOSED_DRAWER_WIDTH = 72 // Enough for icon

const openedMixin = (theme: Theme): CSSObject => ({
  width: DRAWER_WIDTH,
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.enteringScreen,
  }),
  overflowX: 'hidden',
})

const closedMixin = (theme: Theme): CSSObject => ({
  transition: theme.transitions.create('width', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  overflowX: 'hidden',
  width: `calc(${theme.spacing(7)} + 1px)`,
  [theme.breakpoints.up('sm')]: {
    width: `calc(${theme.spacing(9)} + 1px)`,
  },
})

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'flex-end',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
}))

const MiniDrawer = styled(Drawer, { shouldForwardProp: (prop) => prop !== 'open' })(
  ({ theme, open }) => ({
    width: DRAWER_WIDTH,
    flexShrink: 0,
    whiteSpace: 'nowrap',
    boxSizing: 'border-box',
    ...(open && {
      ...openedMixin(theme),
      '& .MuiDrawer-paper': openedMixin(theme),
    }),
    ...(!open && {
      ...closedMixin(theme),
      '& .MuiDrawer-paper': closedMixin(theme),
    }),
  })
)

const MainLayout = () => {
  const theme = useTheme()
  const { toggleTheme, mode } = useThemeContext()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [mobileOpen, setMobileOpen] = useState(false)
  const [open, setOpen] = useState(true) // Desktop expand state

  const navigate = useNavigate()
  const location = useLocation()

  const handleDrawerToggle = () => {
    if (isMobile) {
      setMobileOpen(!mobileOpen)
    } else {
      setOpen(!open)
    }
  }

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Providers', icon: <PeopleIcon />, path: '/admin/providers' },
    { text: 'Payments', icon: <PaymentIcon />, path: '/admin/payments' },
  ]

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', mt: 2 }}>

      {/* Brand Title (Hide when closed on desktop) */}
      {(open || isMobile) && (
        <Box sx={{ px: 2, mb: 2 }}>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}
          >
            Payroll System
          </Typography>
        </Box>
      )}

      <List sx={{ px: 1, flexGrow: 1 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.text}
            selected={location.pathname === item.path}
            onClick={() => {
              navigate(item.path)
              if (isMobile) setMobileOpen(false)
            }}
            sx={{
              minHeight: 48,
              justifyContent: open ? 'initial' : 'center',
              px: 2.5,
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: open ? 3 : 'auto',
                justifyContent: 'center',
              }}
            >
              {item.icon}
            </ListItemIcon>
            <ListItemText primary={item.text} sx={{ opacity: open ? 1 : 0 }} />
          </ListItemButton>
        ))}
      </List>
      <Box sx={{ p: 2, borderTop: '1px solid #f0f0f0' }}>
        <ListItemButton
          onClick={() => alert('Logout clicked')}
          sx={{
            minHeight: 48,
            justifyContent: open ? 'initial' : 'center',
            px: 2.5,
          }}
        >
          <ListItemIcon
            sx={{
              minWidth: 0,
              mr: open ? 3 : 'auto',
              justifyContent: 'center',
            }}
          >
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText primary="Logout" sx={{ opacity: open ? 1 : 0 }} />
        </ListItemButton>
      </Box>
    </Box>
  )

  const container = window !== undefined ? () => window.document.body : undefined

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          width: { md: `calc(100% - ${open ? DRAWER_WIDTH : CLOSED_DRAWER_WIDTH}px)` },
          ml: { md: `${open ? DRAWER_WIDTH : CLOSED_DRAWER_WIDTH}px` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(open && {
            width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
            ml: { md: `${DRAWER_WIDTH}px` },
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
          bgcolor: 'background.paper',
          color: 'text.primary',
          boxShadow: 'none',
          borderBottom: '1px solid #f0f0f0',
        }}
      >
        <Toolbar>
          {/* Desktop Menu Toggle (Optional on Appbar if preferred, but usually inside drawer or here) */}
          {/* If we want the button to expand the drawer from closed state, we might need it on AppBar OR rely on the MiniDrawer strip which is always visible */}
          {/* Since we have a mini drawer, the drawer header is always visible for the button */}

          {/* Mobile Menu Toggle */}

          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>


          <Box sx={{ flexGrow: 1 }} />

          <IconButton onClick={toggleTheme} color="inherit" sx={{ mr: 1 }}>
            {mode === 'dark' ? <SunIcon /> : <MoonIcon />}
          </IconButton>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle2">Admin User</Typography>
            <Avatar sx={{ width: 32, height: 32, bgcolor: theme.palette.primary.main }}>A</Avatar>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: open ? DRAWER_WIDTH : CLOSED_DRAWER_WIDTH }, flexShrink: { md: 0 } }}
      >
        {/* Mobile Drawer (Temporary) */}
        <Drawer
          container={container}
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop Drawer (Mini variant) */}
        <MiniDrawer
          variant="permanent"
          open={open}
          sx={{
            display: { xs: 'none', md: 'block' },
          }}
        >
          {drawerContent}
        </MiniDrawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${open ? DRAWER_WIDTH : CLOSED_DRAWER_WIDTH}px)` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          minHeight: '100vh',
          bgcolor: 'background.default',
        }}
      >
        <DrawerHeader /> {/* Spacer for AppBar */}
        <Outlet />
      </Box>
    </Box>
  )
}

export default MainLayout
