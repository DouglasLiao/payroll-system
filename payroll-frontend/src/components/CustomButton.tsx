import { Button, type ButtonProps } from '@mui/material'

export const CustomButton = ({ children, sx, ...props }: ButtonProps) => {
  return (
    <Button
      {...props}
      sx={{
        borderRadius: 2,
        textTransform: 'none',
        fontWeight: 600,
        boxShadow: 'none',
        '&:hover': {
          boxShadow: 'none',
        },
        ...sx,
      }}
    >
      {children}
    </Button>
  )
}
