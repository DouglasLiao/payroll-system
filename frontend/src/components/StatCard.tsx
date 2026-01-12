import {
  Card,
  CardContent,
  Typography,
  Box,
  type SxProps,
  type Theme,
} from '@mui/material'
import { type ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string | number
  color?: string
  icon?: ReactNode
  subtitle?: string
  sx?: SxProps<Theme>
}

/**
 * Reusable statistics card for displaying metrics
 *
 * @example
 * <StatCard
 *   title="Total de Folhas"
 *   value={42}
 *   icon={<ReceiptIcon />}
 * />
 */
export const StatCard = ({
  title,
  value,
  color = 'text.primary',
  icon,
  subtitle,
  sx = {},
}: StatCardProps) => {
  return (
    <Card sx={sx}>
      <CardContent>
        {icon && <Box sx={{ mb: 1, color: 'action.active' }}>{icon}</Box>}

        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>

        <Typography variant="h3" sx={{ color, fontWeight: 700 }}>
          {value}
        </Typography>

        {subtitle && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 0.5, display: 'block' }}
          >
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}
