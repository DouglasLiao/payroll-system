import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1890ff', // Mantis Blue
      light: '#e6f7ff',
      dark: '#096dd9',
    },
    secondary: {
      main: '#52c41a', // Success Green
    },
    background: {
      default: '#f4f6f8', // Soft Gray
      paper: '#ffffff',
    },
    text: {
      primary: '#262626',
      secondary: '#8c8c8c',
    },
  },
  typography: {
    fontFamily: "'Public Sans', 'Roboto', sans-serif",
    h1: { fontSize: '2.5rem', fontWeight: 700 },
    h2: { fontSize: '2rem', fontWeight: 700 },
    h3: { fontSize: '1.75rem', fontWeight: 600 },
    h4: { fontSize: '1.5rem', fontWeight: 600 },
    h5: { fontSize: '1.25rem', fontWeight: 600 },
    h6: { fontSize: '1rem', fontWeight: 600 },
    subtitle1: { fontSize: '0.875rem' },
    subtitle2: { fontSize: '0.75rem', fontWeight: 500, color: '#8c8c8c' },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 600,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.15)', // Mantis Shadow
          border: '1px solid #f0f0f0',
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          '&.Mui-selected': {
            backgroundColor: '#e6f7ff',
            color: '#1890ff',
            '& .MuiListItemIcon-root': {
              color: '#1890ff',
            },
          },
        },
      },
    },
  },
})

export default theme
