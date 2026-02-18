import { useState, useEffect, useRef } from 'react'
import { TextField, InputAdornment } from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'

interface SearchFieldProps {
  value?: string
  onChange?: (value: string) => void
  onSearch?: (value: string) => void
  placeholder?: string
  width?: string | number
  debounceDelay?: number
}

export function SearchField({
  value: controlledValue,
  onChange,
  onSearch,
  placeholder = 'Buscar...',
  width = '100%',
  debounceDelay = 500,
}: SearchFieldProps) {
  const [internalValue, setInternalValue] = useState(controlledValue || '')
  const firstRender = useRef(true)

  useEffect(() => {
    if (controlledValue !== undefined) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setInternalValue(controlledValue)
    }
  }, [controlledValue])

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false
      return
    }

    const handler = setTimeout(() => {
      onSearch?.(internalValue)
    }, debounceDelay)

    return () => {
      clearTimeout(handler)
    }
  }, [internalValue, debounceDelay, onSearch])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInternalValue(newValue)
    onChange?.(newValue)
  }

  return (
    <TextField
      value={internalValue}
      onChange={handleChange}
      placeholder={placeholder}
      size="small"
      sx={{ width }}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon color="action" />
          </InputAdornment>
        ),
      }}
    />
  )
}
