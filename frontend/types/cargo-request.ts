export type CargoRequestStatus = 'new' | 'in_progress' | 'completed' | 'cancelled'

export interface CargoRequestLocation {
  latitude: number
  longitude: number
}

export interface CargoRequest {
  id: number
  client_id: number
  status: CargoRequestStatus

  origin_address: string
  destination_address: string

  cargo_type: string
  weight_kg: number
  volume_m3: number | null
  vehicle_type: string | null

  loading_date: string
  budget: number | null
  comment: string | null

  created_at: string
  updated_at: string
}

export interface CreateCargoRequest {
  origin_address: string
  origin_location: CargoRequestLocation

  destination_address: string
  destination_location: CargoRequestLocation

  cargo_type: string
  weight_kg: number
  volume_m3: number | null
  vehicle_type: string | null

  loading_date: string
  budget: number | null
  comment: string | null
}
