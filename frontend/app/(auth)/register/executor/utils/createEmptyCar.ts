import type { CarFormInput } from '@/schemas/car/carSchema'

export const createEmptyCar = (): CarFormInput => ({
  brand: '',
  model: '',
  cargo_capacity: undefined,
  volume_capacity: undefined,
  car_type: undefined,
  license_plate: '',
  manufacture_year: undefined,
  photo: undefined,
  VIN: '',
})
