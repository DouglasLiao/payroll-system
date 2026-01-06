import { createTheme, type PaletteMode } from '@mui/material'

export const getTheme = (mode: PaletteMode) => {
  const isLight = mode === 'light'

  return createTheme({
    palette: {
      mode,
      primary: {
        main: isLight ? '#4F46E5' : '#6366F1', // Indigo 600 / 500
      },
      background: {
        default: isLight ? '#F8FAFC' : '#020617', // Slate 50 / 950
        paper: isLight ? '#FFFFFF' : '#0F172A', // White / Slate 900
      },
      text: {
        primary: isLight ? '#0F172A' : '#F8FAFC', // Slate 900 / 50
        secondary: isLight ? '#64748B' : '#94A3B8', // Slate 500 / 400
      },
      divider: isLight ? '#e2e8f0' : '#1e293b', // Slate 200 / 800 (Custom guess for dividers)
    },
    typography: {
      fontFamily: "'Inter', 'Public Sans', 'Roboto', sans-serif", // Added Inter as it matches the modern look
      h1: { fontSize: '2.5rem', fontWeight: 700, color: isLight ? '#0F172A' : '#F8FAFC' },
      h2: { fontSize: '2rem', fontWeight: 700, color: isLight ? '#0F172A' : '#F8FAFC' },
      h3: { fontSize: '1.75rem', fontWeight: 600, color: isLight ? '#0F172A' : '#F8FAFC' },
      h4: { fontSize: '1.5rem', fontWeight: 600, color: isLight ? '#0F172A' : '#F8FAFC' },
      h5: { fontSize: '1.25rem', fontWeight: 600, color: isLight ? '#0F172A' : '#F8FAFC' },
      h6: { fontSize: '1rem', fontWeight: 600, color: isLight ? '#0F172A' : '#F8FAFC' },
      subtitle1: { fontSize: '0.875rem', color: isLight ? '#64748B' : '#94A3B8' },
      subtitle2: { fontSize: '0.75rem', fontWeight: 500, color: isLight ? '#64748B' : '#94A3B8' },
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
            boxShadow:
              mode === 'light'
                ? '0px 1px 3px rgba(0, 0, 0, 0.1), 0px 1px 2px rgba(0, 0, 0, 0.06)' // Slate subtle shadow
                : '0px 1px 3px rgba(0, 0, 0, 0.5), 0px 1px 2px rgba(0, 0, 0, 0.3)', // Darker shadow
            border: mode === 'light' ? '1px solid #e2e8f0' : '1px solid #1e293b',
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
              backgroundColor: isLight ? '#EEF2FF' : 'rgba(99, 102, 241, 0.16)', // Indigo 50
              color: isLight ? '#4F46E5' : '#818CF8', // Indigo 600 / 400
              '& .MuiListItemIcon-root': {
                color: isLight ? '#4F46E5' : '#818CF8',
              },
            },
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderBottom: `1px solid ${isLight ? '#e2e8f0' : '#1e293b'}`,
          },
        },
      },
    },
  })
}
