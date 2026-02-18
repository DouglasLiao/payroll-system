import { TextField, type TextFieldProps } from '@mui/material'
import { forwardRef } from 'react'
import { formatCPF, formatCNPJ } from 'src/utils/validators'

/**
 * CPF Input with automatic formatting mask (000.000.000-00)
 */
export const CPFInput = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ value, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const cleaned = e.target.value.replace(/\D/g, '')
      if (cleaned.length <= 11) {
        const formatted = formatCPF(cleaned)
        if (onChange) {
          // Create synthetic event with formatted value
          const syntheticEvent = {
            ...e,
            target: { ...e.target, value: formatted },
          }
          onChange(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
        }
      }
    }

    return (
      <TextField
        {...props}
        ref={ref}
        value={value}
        onChange={handleChange}
        placeholder="000.000.000-00"
        inputProps={{
          maxLength: 14,
          ...props.inputProps,
        }}
      />
    )
  }
)

CPFInput.displayName = 'CPFInput'

/**
 * CNPJ Input with automatic formatting mask (00.000.000/0000-00)
 */
export const CNPJInput = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ value, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const cleaned = e.target.value.replace(/\D/g, '')
      if (cleaned.length <= 14) {
        const formatted = formatCNPJ(cleaned)
        if (onChange) {
          const syntheticEvent = {
            ...e,
            target: { ...e.target, value: formatted },
          }
          onChange(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
        }
      }
    }

    return (
      <TextField
        {...props}
        ref={ref}
        value={value}
        onChange={handleChange}
        placeholder="00.000.000/0000-00"
        inputProps={{
          maxLength: 18,
          ...props.inputProps,
        }}
      />
    )
  }
)

CNPJInput.displayName = 'CNPJInput'

/**
 * Currency Input with Brazilian Real formatting
 */
export const CurrencyInput = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ value, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      // Remove all non-numeric characters
      const cleaned = e.target.value.replace(/\D/g, '')

      // Convert to number and format
      if (cleaned === '') {
        if (onChange) {
          const syntheticEvent = {
            ...e,
            target: { ...e.target, value: '' },
          }
          onChange(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
        }
        return
      }

      // Parse as cents
      const numValue = parseInt(cleaned, 10) / 100

      // Format as currency
      const formatted = numValue.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })

      if (onChange) {
        const syntheticEvent = {
          ...e,
          target: { ...e.target, value: formatted },
        }
        onChange(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
      }
    }

    return (
      <TextField
        {...props}
        ref={ref}
        value={value}
        onChange={handleChange}
        placeholder="0,00"
        InputProps={{
          startAdornment: <span style={{ marginRight: 4 }}>R$</span>,
          ...props.InputProps,
        }}
      />
    )
  }
)

CurrencyInput.displayName = 'CurrencyInput'

/**
 * Phone Input with Brazilian phone mask
 */
export const PhoneInput = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ value, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const cleaned = e.target.value.replace(/\D/g, '')

      let formatted = cleaned
      if (cleaned.length <= 10) {
        // (00) 0000-0000
        formatted = cleaned
          .replace(/(\d{2})(\d)/, '($1) $2')
          .replace(/(\d{4})(\d)/, '$1-$2')
      } else {
        // (00) 00000-0000
        formatted = cleaned
          .replace(/(\d{2})(\d)/, '($1) $2')
          .replace(/(\d{5})(\d)/, '$1-$2')
      }

      if (onChange) {
        const syntheticEvent = {
          ...e,
          target: { ...e.target, value: formatted },
        }
        onChange(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
      }
    }

    return (
      <TextField
        {...props}
        ref={ref}
        value={value}
        onChange={handleChange}
        placeholder="(00) 00000-0000"
        inputProps={{
          maxLength: 15,
          ...props.inputProps,
        }}
      />
    )
  }
)

PhoneInput.displayName = 'PhoneInput'
