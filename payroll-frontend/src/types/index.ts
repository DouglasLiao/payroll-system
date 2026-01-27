export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type PaymentMethod = 'PIX' | 'TED' | 'TRANSFER'
export type PaymentStatus = 'PENDING' | 'PAID' | 'CANCELLED'
export type PayrollStatus = 'DRAFT' | 'CLOSED' | 'PAID'
export type ItemType = 'CREDIT' | 'DEBIT'

export interface Provider {
  id: number
  name: string
  role: string
  salary_base?: string // Mantido por compatibilidade
  monthly_value: string
  monthly_hours: number
  advance_enabled: boolean
  advance_percentage: string
  vt_value: string
  payment_method: PaymentMethod
  pix_key?: string
  bank_name?: string
  bank_agency?: string
  bank_account?: string
  email?: string
  description?: string
}

export interface Payment {
  id: number
  provider: number
  provider_name?: string
  reference: string
  amount_base: string
  bonus: string
  discounts: string
  total_calculated: string
  status: PaymentStatus
  paid_at?: string
}

export interface PayrollItem {
  id: number
  type: ItemType
  type_display: string
  description: string
  amount: string
}

export interface Payroll {
  id: number
  provider: number
  provider_name: string
  reference_month: string
  status: PayrollStatus
  status_display: string

  // Valores base
  base_value: string
  hourly_rate: string
  advance_value: string
  remaining_value: string

  // Horas
  overtime_hours_50: string
  holiday_hours: string
  night_hours: string
  late_minutes: number
  absence_hours: string

  // Descontos variáveis
  manual_discounts: string
  vt_discount: string

  // Valores calculados - Proventos
  overtime_amount: string
  holiday_amount: string
  dsr_amount: string
  night_shift_amount: string
  total_earnings: string

  // Valores calculados - Descontos
  late_discount: string
  absence_discount: string
  dsr_on_absences: string
  total_discounts: string

  // Totais
  gross_value: string
  net_value: string

  // Metadados
  notes?: string
  closed_at?: string
  paid_at?: string
  created_at: string
  updated_at: string
}

export interface PayrollDetail extends Omit<Payroll, 'provider'> {
  items: PayrollItem[]
  provider: {
    id: number
    name: string
    role: string
    monthly_value: string
  }
}

export interface PayrollCreateData {
  provider_id: number
  reference_month: string
  overtime_hours_50?: number
  holiday_hours?: number
  night_hours?: number
  late_minutes?: number
  absence_hours?: number
  manual_discounts?: number
  advance_already_paid?: number
  notes?: string
}

export interface DashboardStats {
  stats: {
    pending: number
    paid: number
  }
  recent_activity: Payment[]
}

// Enhanced dashboard stats with aggregations and trends
export interface EnhancedDashboardStats {
  stats: {
    total_providers: number
    payrolls: {
      total: number
      draft: number
      closed: number
      paid: number
    }
    financial: {
      total_value: number
      pending_value: number
      paid_value: number
      average_payroll: number
    }
  }
  monthly_aggregation: {
    [month: string]: {
      draft: { count: number; value: number }
      closed: { count: number; value: number }
      paid: { count: number; value: number }
      // Derived fields calculated by backend
      total_count: number
      total_value: number
      avg_value: number
    }
  }
  trends: {
    monthly_growth_percentage: number
    period_vs_previous: {
      payrolls_change: number
      value_change: number
    }
  }
  recent_activity: Payroll[]
}

// Dashboard component types
export interface PayrollStats {
  total: number
  drafts: number
  closed: number
  paid: number
  totalValue: number
  avgValue: number
}

export interface MonthlyData {
  [month: string]: {
    draft: number
    closed: number
    paid: number
    total: number
    draftValue: number
    closedValue: number
    paidValue: number
  }
}

export interface FinancialMetrics {
  monthlyGrowth: number
  avgMonthlyValue: number
  projectedNextMonth: number
  totalPending: number
  totalPaid: number
  cashFlow: number
}

export interface ChartPeriod {
  value: 3 | 6 | 12
  label: string
}
