import { VehicleType, CarType } from '../consts/vehicleTypes'
import { CarBrand } from '@/consts/carBrands'
import type { MediaItem } from './slider'

type VehicleBase = {
  type: VehicleType
  brand: CarBrand
  model: string
  cargo_capacity: number
  volume_capacity: number | null
  car_type: CarType | null
  license_plate: string
  manufacture_year: number
  price_per_km?: string | number | null
  VIN: string | null
}

export type VehicleCreate = VehicleBase

export interface Car extends VehicleBase {
  id: number
  executor_id: number
  is_deleted: boolean
  photos: MediaItem[]
}
