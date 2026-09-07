import { Car } from './car'
export interface Executor {
  id: number
  name: string
  email: string
  phone_number: string
  image?: string
  type: 'carrier' | 'supplier' | 'service'
  price_per_km: number | null
  is_notifications_enabled: boolean
  is_active: boolean
  membership: string
  subscription?: {
    membership: {
      name: string
    }
  } | null
  car?: Car
  supplier?: Supplier
  service?: Service
}

interface Supplier {
  legal_name: string
  unp: string
  address: string
}

interface Service {
  legal_name: string
  unp: string
  address: string
  supportedCars: Car[]
}
