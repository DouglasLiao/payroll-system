import { useState } from 'react'
import {
  Card,
  CardContent,
  TextField,
  MenuItem,
  Button,
  Box,
  Chip,
  Typography,
  Collapse,
  IconButton,
  InputAdornment,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material'
import type { SelectChangeEvent } from '@mui/material'
import {
  FilterList,
  ExpandMore,
  ExpandLess,
  Clear,
  Search,
} from '@mui/icons-material'
import type { Provider } from '../types'

export interface PayrollFilters {
  status: string
  reference_month: string
  provider?: number
}

interface PayrollFiltersComponentProps {
  filters: PayrollFilters
  onFiltersChange: (filters: PayrollFilters) => void
  providers?: Provider[]
}

export const PayrollFiltersComponent = ({
  filters,
  onFiltersChange,
  providers = [],
}: PayrollFiltersComponentProps) => {
  const [expanded, setExpanded] = useState(true)

  const handleClearFilters = () => {
    onFiltersChange({
      status: 'all',
      reference_month: '',
      provider: undefined,
    })
  }

  const handleStatusChange = (event: SelectChangeEvent) => {
    onFiltersChange({ ...filters, status: event.target.value })
  }

  const handleMonthChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, reference_month: event.target.value })
  }

  const handleProviderChange = (event: SelectChangeEvent<number | string>) => {
    const value = event.target.value
    onFiltersChange({
      ...filters,
      provider: value === '' ? undefined : Number(value),
    })
  }

  // Conta quantos filtros estão ativos
  const activeFiltersCount =
    (filters.status !== 'all' ? 1 : 0) +
    (filters.reference_month ? 1 : 0) +
    (filters.provider ? 1 : 0)

  return (
    <Card
      elevation={2}
      sx={{
        borderRadius: 2,
        border: '1px solid',
        borderColor: 'divider',
        overflow: 'hidden',
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: expanded ? 2 : 0,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterList color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Filtros
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 1 }}>
            {activeFiltersCount > 0 && (
              <Button
                size="small"
                variant="outlined"
                startIcon={<Clear />}
                onClick={handleClearFilters}
                sx={{ textTransform: 'none' }}
              >
                Limpar
              </Button>
            )}
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
              sx={{
                transform: expanded ? 'rotate(0deg)' : 'rotate(180deg)',
                transition: 'transform 0.3s',
              }}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>

        {/* Filtros */}
        <Collapse in={expanded}>
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(4, 1fr)',
              },
              gap: 2,
            }}
          >
            {/* Status */}
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                label="Status"
                onChange={handleStatusChange}
              >
                <MenuItem value="all">
                  <em>Todos os Status</em>
                </MenuItem>
                <MenuItem value="DRAFT">
                  <Chip
                    size="small"
                    label="Rascunho"
                    color="warning"
                    variant="filled"
                    sx={{ mr: 1 }}
                  />
                  Rascunho
                </MenuItem>
                <MenuItem value="CLOSED">
                  <Chip
                    size="small"
                    label="Fechada"
                    color="info"
                    variant="filled"
                    sx={{ mr: 1 }}
                  />
                  Fechada
                </MenuItem>
                <MenuItem value="PAID">
                  <Chip
                    size="small"
                    label="Paga"
                    color="success"
                    variant="filled"
                    sx={{ mr: 1 }}
                  />
                  Paga
                </MenuItem>
              </Select>
            </FormControl>

            {/* Mês de Referência */}
            <TextField
              label="Mês de Referência"
              type="month"
              value={filters.reference_month}
              onChange={handleMonthChange}
              size="small"
              fullWidth
              InputLabelProps={{ shrink: true }}
              InputProps={{
                endAdornment: filters.reference_month && (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={() =>
                        onFiltersChange({ ...filters, reference_month: '' })
                      }
                    >
                      <Clear fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            {/* Prestador */}
            <FormControl fullWidth size="small">
              <InputLabel>Prestador</InputLabel>
              <Select
                value={filters.provider || ''}
                label="Prestador"
                onChange={handleProviderChange}
                startAdornment={
                  <InputAdornment position="start">
                    <Search fontSize="small" color="action" />
                  </InputAdornment>
                }
              >
                <MenuItem value="">
                  <em>Todos os Prestadores</em>
                </MenuItem>
                {providers.map((provider) => (
                  <MenuItem key={provider.id} value={provider.id}>
                    {provider.name} - {provider.role}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Espaço para mais filtros futuros */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
              }}
            >
              {activeFiltersCount > 0 && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: { xs: 'none', md: 'block' } }}
                >
                  {activeFiltersCount} filtro{activeFiltersCount > 1 ? 's' : ''}{' '}
                  aplicado{activeFiltersCount > 1 ? 's' : ''}
                </Typography>
              )}
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  )
}
