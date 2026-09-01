export interface Client {
  id: number
  name: string
  email: string
  phone_number: string
  VIN_code: string | null
  is_notifications_enabled: boolean
  is_active: boolean
}
