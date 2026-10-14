import type { CarType } from '@/schemas/car/carSchema'

export type EmptyCarForm = {
  brand: string
  model: string
  cargo_capacity?: number
  volume_capacity?: number
  car_type?: CarType
  license_plate: string
  manufacture_year?: number
  photos?: File[]
  VIN?: string
}

export const createEmptyCar = (): EmptyCarForm => ({
  brand: '',
  model: '',
  cargo_capacity: undefined,
  volume_capacity: undefined,
  car_type: undefined,
  license_plate: '',
  manufacture_year: undefined,
  photos: [],
  VIN: '',
})
