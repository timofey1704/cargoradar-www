import type { CarFormOutput } from '@/schemas/car/carSchema'

export const createEmptyCar = (): CarFormOutput => ({
  brand: '',
  model: '',
  cargo_capacity: 0,
  volume_capacity: 0,
  car_type: 'sedan',
  license_plate: '',
  manufacture_year: 2024,
  photo: undefined,
  VIN: '',
})
