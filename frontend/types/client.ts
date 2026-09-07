// Базовые поля
interface BaseClient {
  id: number
  name: string
  email: string
  phone_number: string
  image?: string
  VIN_code: string | null
  membership?: string
  is_notifications_enabled: boolean
  is_active: boolean
  subscription?: {
    membership: {
      name: string
    }
  } | null
}

interface LegalFields {
  legal_name: string
  unp: string
  address: string
}

// юнион
export type Client = BaseClient & ({ type: 'individual' } | ({ type: 'legal' } & LegalFields))
