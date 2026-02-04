import React from 'react'
import { Controller, type Control } from 'react-hook-form'
import { TextField, type SxProps } from '@mui/material'
import type { PayrollFormInputs } from '../sections/ContractDataSection'

interface NumericFieldProps {
  name: keyof PayrollFormInputs
  label: string
  control: Control<PayrollFormInputs>
  placeholder?: string
  helperText?: string
  disabled?: boolean
  sx?: SxProps
}

export const NumericField: React.FC<NumericFieldProps> = ({
  name,
  label,
  control,
  placeholder = '0',
  helperText,
  disabled = false,
  sx,
}) => {
  const handleNumericChange =
    (field: { onChange: (value: number) => void }) =>
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const val = e.target.value
      field.onChange(val === '' ? 0 : parseFloat(val) || 0)
    }

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <TextField
          {...field}
          label={label}
          fullWidth
          value={field.value || ''}
          onChange={handleNumericChange(field)}
          placeholder={placeholder}
          helperText={helperText}
          disabled={disabled}
          autoComplete="off"
          sx={{
            '& .MuiInputBase-root': {
              bgcolor: 'background.paper',
            },
            ...sx,
          }}
        />
      )}
    />
  )
}
