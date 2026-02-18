import {
  Card,
  CardContent,
  Typography,
  Box,
  Skeleton,
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
  loading?: boolean
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
 *   loading={isLoading}
 * />
 */
export const StatCard = ({
  title,
  value,
  color = 'text.primary',
  icon,
  subtitle,
  loading = false,
  sx = {},
}: StatCardProps) => {
  return (
    <Card sx={sx}>
      <CardContent>
        {icon && <Box sx={{ mb: 1, color: 'action.active' }}>{icon}</Box>}

        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {title}
        </Typography>

        {loading ? (
          <Skeleton variant="text" height={48} width="60%" />
        ) : (
          <Typography variant="h3" sx={{ color, fontWeight: 700 }}>
            {value}
          </Typography>
        )}

        {subtitle && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 0.5, display: 'block' }}
          >
            {loading ? <Skeleton variant="text" width="80%" /> : subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}
