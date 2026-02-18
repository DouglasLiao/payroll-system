import { useState } from 'react'
import {
  Card,
  CardContent,
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
  Autocomplete,
  TextField,
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
import type { Provider } from 'src/types'
import { CustomMenuItem } from 'src/components/menu/CustomMenuItem'

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

  // Initialize local state once from props - no need to sync via useEffect
  // The "Apply Filters" button pattern means local state is independent until applied
  const [localFilters, setLocalFilters] = useState<PayrollFilters>(
    () => filters
  )

  // Local state for draft filters
  const [selectedMonth, setSelectedMonth] = useState<Dayjs | null>(() => {
    if (filters.reference_month) {
      const [month, year] = filters.reference_month.split('/')
      return dayjs(`${year}-${month}-01`)
    }
    return null
  })

  const handleApplyFilters = () => {
    onFiltersChange(localFilters)
  }

  const handleClearFilters = () => {
    const clearedFilters = {
      status: 'all',
      reference_month: '',
      provider: undefined,
    }
    setLocalFilters(clearedFilters)
    setSelectedMonth(null)
    onFiltersChange(clearedFilters)
  }

  const handleStatusChange = (event: SelectChangeEvent) => {
    setLocalFilters({ ...localFilters, status: event.target.value })
  }

  const handleMonthChange = (value: Dayjs | null) => {
    setSelectedMonth(value)
    if (value) {
      const formattedMonth = value.format('MM/YYYY')
      setLocalFilters({ ...localFilters, reference_month: formattedMonth })
    } else {
      setLocalFilters({ ...localFilters, reference_month: '' })
    }
  }

  const handleProviderChange = (newValue: Provider | null) => {
    setLocalFilters({
      ...localFilters,
      provider: newValue?.id || undefined,
    })
  }

  // Conta quantos filtros estão ativos (usando localFilters)
  const activeFiltersCount =
    (localFilters.status !== 'all' ? 1 : 0) +
    (localFilters.reference_month ? 1 : 0) +
    (localFilters.provider ? 1 : 0)

  // Check if filters have changed
  const hasChanges =
    localFilters.status !== filters.status ||
    localFilters.reference_month !== filters.reference_month ||
    localFilters.provider !== filters.provider

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
                <CustomMenuItem value="all">
                  <em>Todos os Status</em>
                </CustomMenuItem>
                <CustomMenuItem value="DRAFT">
                  <Chip
                    size="small"
                    label="Rascunho"
                    color="warning"
                    variant="filled"
                    sx={{ mr: 1 }}
                  />
                  Rascunho
                </CustomMenuItem>
                <CustomMenuItem value="CLOSED">
                  <Chip
                    size="small"
                    label="Fechada"
                    color="info"
                    variant="filled"
                    sx={{ mr: 1 }}
                  />
                  Fechada
                </CustomMenuItem>
                <CustomMenuItem value="PAID">
                  <Chip
                    size="small"
                    label="Paga"
                    color="success"
                    variant="filled"
                    sx={{ mr: 1 }}
                  />
                  Paga
                </CustomMenuItem>
              </Select>
            </FormControl>

            {/* Mês de Referência */}
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

            {/* Prestador */}
            <Autocomplete
              options={providers || []}
              getOptionLabel={(option) => `${option.name} - ${option.role}`}
              value={
                providers?.find((p) => p.id === localFilters.provider) || null
              }
              onChange={(_, newValue) => handleProviderChange(newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Prestador"
                  size="small"
                  placeholder="Buscar prestador..."
                  InputProps={{
                    ...params.InputProps,
                    startAdornment: (
                      <>
                        <InputAdornment position="start">
                          <Search fontSize="small" color="action" />
                        </InputAdornment>
                        {params.InputProps.startAdornment}
                      </>
                    ),
                  }}
                />
              )}
              noOptionsText="Nenhum prestador encontrado"
              loadingText="Carregando..."
              isOptionEqualToValue={(option, value) => option.id === value.id}
            />

            {/* Apply Filters Button */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'flex-end',
                gap: 1,
              }}
            >
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
              </Button>
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  )
}
