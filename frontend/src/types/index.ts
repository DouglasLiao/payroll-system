export type PaymentMethod = 'PIX' | 'TED' | 'TRANSFER'
export type PaymentStatus = 'PENDING' | 'PAID' | 'CANCELLED'

export interface Provider {
  id: number
  name: string
  role: string
  salary_base: string // Decimal comes as string from API usually, or number
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
  provider_name?: string // Read only
  reference: string
  amount_base: string
  bonus: string
  discounts: string
  total_calculated: string
  status: PaymentStatus
  paid_at?: string
}

export interface DashboardStats {
  stats: {
    pending: number
    paid: number
  }
  recent_activity: Payment[]
}
