import { Chip, type ChipProps } from '@mui/material'

/**
 * Status types for different entities in the system
 */
export type PaymentStatus = 'PENDING' | 'PAID' | 'CANCELLED'
export type PayrollStatus = 'DRAFT' | 'CLOSED' | 'PAID'

type AllStatusTypes = PaymentStatus | PayrollStatus

interface StatusConfig {
  label: string
  color: ChipProps['color']
}

/**
 * Configuration mapping for all possible statuses
 */
const STATUS_CONFIG: Record<AllStatusTypes, StatusConfig> = {
  // Payment statuses
  PENDING: { label: 'Pendente', color: 'warning' },
  PAID: { label: 'Paga', color: 'success' },
  CANCELLED: { label: 'Cancelada', color: 'error' },

  // Payroll statuses
  DRAFT: { label: 'Rascunho', color: 'warning' },
  CLOSED: { label: 'Fechada', color: 'info' },
}

interface StatusChipProps {
  status: AllStatusTypes
  label?: string
  size?: 'small' | 'medium'
}

/**
 * Reusable status chip component with consistent styling across the app
 *
 * @example
 * <StatusChip status="PAID" />
 * <StatusChip status="DRAFT" label="Em edição" />
 */
export const StatusChip = ({
  status,
  label,
  size = 'small',
}: StatusChipProps) => {
  const config = STATUS_CONFIG[status]

  return <Chip label={label || config.label} color={config.color} size={size} />
}
