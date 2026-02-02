import { useState, useEffect } from 'react'
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
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import dayjs, { Dayjs } from 'dayjs'
import 'dayjs/locale/pt-br'
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

  // Local state for draft filters
  const [localFilters, setLocalFilters] = useState<PayrollFilters>(filters)
  const [selectedMonth, setSelectedMonth] = useState<Dayjs | null>(
    filters.reference_month
      ? (() => {
          const [month, year] = filters.reference_month.split('/')
          return dayjs(`${year}-${month}-01`)
        })()
      : null
  )

  // Sync local state when external filters change
  useEffect(() => {
    setLocalFilters(filters)

    // Update selectedMonth when reference_month changes
    if (filters.reference_month) {
      const [month, year] = filters.reference_month.split('/')
      setSelectedMonth(dayjs(`${year}-${month}-01`))
    } else {
      setSelectedMonth(null)
    }
  }, [filters])

  const handleClearFilters = () => {
<<<<<<< Updated upstream
    const emptyFilters = {
=======
    const clearedFilters = {
>>>>>>> Stashed changes
      status: 'all',
      reference_month: '',
      provider: undefined,
    }
<<<<<<< Updated upstream
    setLocalFilters(emptyFilters)
    onFiltersChange(emptyFilters)
=======
    setLocalFilters(clearedFilters)
    setSelectedMonth(null)
    onFiltersChange(clearedFilters)
>>>>>>> Stashed changes
  }

  const handleStatusChange = (event: SelectChangeEvent) => {
    setLocalFilters({ ...localFilters, status: event.target.value })
  }

<<<<<<< Updated upstream
  const handleMonthChange = (newValue: dayjs.Dayjs | null) => {
    setLocalFilters({
      ...localFilters,
      reference_month: newValue ? newValue.format('YYYY-MM') : '',
    })
=======
  const handleMonthChange = (value: Dayjs | null) => {
    setSelectedMonth(value)
    if (value) {
      const formattedMonth = value.format('MM/YYYY')
      setLocalFilters({ ...localFilters, reference_month: formattedMonth })
    } else {
      setLocalFilters({ ...localFilters, reference_month: '' })
    }
>>>>>>> Stashed changes
  }

  const handleProviderChange = (event: SelectChangeEvent<number | string>) => {
    const value = event.target.value
    setLocalFilters({
      ...localFilters,
      provider: value === '' ? undefined : Number(value),
    })
  }

<<<<<<< Updated upstream
  // Conta quantos filtros estão ativos (baseado no localFilters)
=======
  const handleApplyFilters = () => {
    onFiltersChange(localFilters)
  }

  // Conta quantos filtros estão ativos (usando localFilters)
>>>>>>> Stashed changes
  const activeFiltersCount =
    (localFilters.status !== 'all' ? 1 : 0) +
    (localFilters.reference_month ? 1 : 0) +
    (localFilters.provider ? 1 : 0)
<<<<<<< Updated upstream
=======

  // Check if filters have changed
  const hasChanges =
    localFilters.status !== filters.status ||
    localFilters.reference_month !== filters.reference_month ||
    localFilters.provider !== filters.provider
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
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
=======
            <LocalizationProvider
              dateAdapter={AdapterDayjs}
              adapterLocale="pt-br"
            >
              <DatePicker
                label="Mês de Referência"
                views={['month', 'year']}
                value={selectedMonth}
                onChange={handleMonthChange}
                slotProps={{
                  textField: {
                    size: 'small',
                    fullWidth: true,
                    InputProps: {
                      endAdornment: selectedMonth && (
                        <InputAdornment position="end">
                          <IconButton
                            size="small"
                            edge="end"
                            onClick={() => {
                              setSelectedMonth(null)
                              setLocalFilters({
                                ...localFilters,
                                reference_month: '',
                              })
                            }}
                          >
                            <Clear fontSize="small" />
                          </IconButton>
                        </InputAdornment>
                      ),
                    },
                  },
                }}
              />
            </LocalizationProvider>
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
            {/* Espaço para Botão Filtrar */}
=======
            {/* Apply Filters Button */}
>>>>>>> Stashed changes
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                gap: 1,
              }}
            >
<<<<<<< Updated upstream
              <Button
                variant="contained"
                onClick={handleApplyFilters}
                fullWidth
                sx={{ height: 40 }}
              >
                Filtrar
=======
              {hasChanges && (
                <Typography
                  variant="caption"
                  color="warning.main"
                  sx={{ display: { xs: 'none', md: 'block' } }}
                >
                  Há alterações não aplicadas
                </Typography>
              )}
              <Button
                variant="contained"
                size="small"
                onClick={handleApplyFilters}
                disabled={!hasChanges}
                sx={{
                  textTransform: 'none',
                  minWidth: 120,
                }}
              >
                Aplicar Filtros
>>>>>>> Stashed changes
              </Button>
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  )
}
