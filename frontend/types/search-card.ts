export type SearchCardType = 'carrier' | 'service' | 'supplier'

export interface SearchRoute {
  from: string
  to: string
  comment?: string | null
  price?: number | null
}

export interface SearchVehicle {
  type: string
  brand: string
  model: string
  cargoCapacity: number
  volumeCapacity?: number | null
  carType?: string | null
  manufactureYear: number
  photoUrl?: string | null
  pricePerKm?: number | null
}

export interface SearchCardExecutor {
  id: number
  name: string
  photoUrl?: string | null
  rating?: number | null
  reviewsCount?: number
}

export interface SearchOrganization {
  id: number
  legalName: string
  address: string
  brands: string[]
  photoUrl?: string | null
  rating?: number | null
  reviewsCount?: number
}

interface BaseSearchCardProps {
  href: string
}

export interface CarrierSearchCardProps extends BaseSearchCardProps {
  type: 'carrier'
  executor: SearchCardExecutor
  vehicle: SearchVehicle
  route?: SearchRoute | null
}

export interface OrganizationSearchCardProps extends BaseSearchCardProps {
  type: 'service' | 'supplier'
  organization: SearchOrganization
}

export type SearchCardProps = CarrierSearchCardProps | OrganizationSearchCardProps
