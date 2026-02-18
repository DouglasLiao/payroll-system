import { MenuItem, type MenuItemProps, styled } from '@mui/material'
import { forwardRef } from 'react'

// Licensed, premium feel custom MenuItem
const StyledMenuItem = styled(MenuItem)(({ theme }) => ({
  margin: '4px 8px',
  borderRadius: '8px',
  padding: '10px 16px',
  transition: 'all 0.2s ease-in-out',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
    transform: 'translateX(4px)',
  },
  '&.Mui-selected': {
    backgroundColor: theme.palette.primary.light,
    color: theme.palette.primary.contrastText,
    '&:hover': {
      backgroundColor: theme.palette.primary.main,
    },
  },
}))

export const CustomMenuItem = forwardRef<HTMLLIElement, MenuItemProps>(
  (props, ref) => {
    return <StyledMenuItem ref={ref} {...props} />
  }
)

CustomMenuItem.displayName = 'CustomMenuItem'
