export interface Client {
  id: number
  name: string
  email: string
  phone_number: string
  image?: string
  type: 'individual' | 'legal'
  VIN_code: string | null
  membership?: 'free' | 'premium'
  is_notifications_enabled: boolean
  is_active: boolean
}
