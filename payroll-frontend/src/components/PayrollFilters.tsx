import { useState } from 'react'
import {
  Card,
  CardContent,
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
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import dayjs from 'dayjs'
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
  const [localFilters, setLocalFilters] = useState<PayrollFilters>(filters)

  const handleApplyFilters = () => {
    onFiltersChange(localFilters)
  }

  const handleClearFilters = () => {
    const emptyFilters = {
      status: 'all',
      reference_month: '',
      provider: undefined,
    }
    setLocalFilters(emptyFilters)
    onFiltersChange(emptyFilters)
  }

  const handleStatusChange = (event: SelectChangeEvent) => {
    setLocalFilters({ ...localFilters, status: event.target.value })
  }

  const handleMonthChange = (newValue: dayjs.Dayjs | null) => {
    setLocalFilters({
      ...localFilters,
      reference_month: newValue ? newValue.format('YYYY-MM') : '',
    })
  }

  const handleProviderChange = (event: SelectChangeEvent<number | string>) => {
    const value = event.target.value
    setLocalFilters({
      ...localFilters,
      provider: value === '' ? undefined : Number(value),
    })
  }

  // Conta quantos filtros estão ativos (baseado no localFilters)
  const activeFiltersCount =
    (localFilters.status !== 'all' ? 1 : 0) +
    (localFilters.reference_month ? 1 : 0) +
    (localFilters.provider ? 1 : 0)

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
                value={localFilters.status}
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
            {/* Mês de Referência */}
            {/* Mês de Referência */}
            <DatePicker
              label="Mês de Referência"
              format="MM/YYYY"
              views={['month', 'year']}
              value={
                localFilters.reference_month
                  ? dayjs(localFilters.reference_month)
                  : null
              }
              onChange={handleMonthChange}
              slotProps={{
                textField: {
                  size: 'small',
                  fullWidth: true,
                  InputProps: {
                    endAdornment: localFilters.reference_month && (
                      <InputAdornment position="end">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation()
                            setLocalFilters({
                              ...localFilters,
                              reference_month: '',
                            })
                          }}
                          edge="end"
                        >
                          <Clear fontSize="small" />
                        </IconButton>
                      </InputAdornment>
                    ),
                  },
                },
              }}
            />

            {/* Prestador */}
            <FormControl fullWidth size="small">
              <InputLabel>Prestador</InputLabel>
              <Select
                value={localFilters.provider || ''}
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

            {/* Espaço para Botão Filtrar */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
              }}
            >
              <Button
                variant="contained"
                onClick={handleApplyFilters}
                fullWidth
                sx={{ height: 40 }}
              >
                Filtrar
              </Button>
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  )
}
