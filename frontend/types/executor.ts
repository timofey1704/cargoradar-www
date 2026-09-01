export interface Executor {
  id: number
  name: string
  email: string
  phone_number: string
  type: string
  price_per_km: number | null
  is_notifications_enabled: boolean
  is_active: boolean
}
