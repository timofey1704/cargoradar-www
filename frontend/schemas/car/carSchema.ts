import { z } from 'zod'

export const CarTypes = {
  sedan: 'sedan',
  hatchback: 'hatchback',
  coupe: 'coupe',
  convertible: 'convertible',
  suv: 'suv',
  crossover: 'crossover',
  minivan: 'minivan',
  van: 'van',
  pickup: 'pickup',
} as const

export const carTypeSchema = z.enum([
  'sedan',
  'hatchback',
  'coupe',
  'convertible',
  'suv',
  'crossover',
  'minivan',
  'van',
  'pickup',
])

export type CarType = z.infer<typeof carTypeSchema>

export const CarTypesNames: Record<CarType, string> = {
  sedan: 'Седан',
  hatchback: 'Хэтчбек',
  coupe: 'Купе',
  convertible: 'Кабриолет',
  suv: 'Внедорожник',
  crossover: 'Кроссовер',
  minivan: 'Минивэн',
  van: 'Фургон',
  pickup: 'Пикап',
}

export const carSchema = z.object({
  brand: z.string().min(1, 'Выберите марку автомобиля'),

  model: z.string().min(1, 'Введите модель автомобиля'),

  cargo_capacity: z
    .number()
    .int('Грузоподъёмность должна быть целым числом')
    .gt(0, 'Грузоподъёмность должна быть больше 0'),

  volume_capacity: z
    .number()
    .int('Объём должен быть целым числом')
    .gt(0, 'Объём должен быть больше 0')
    .optional(),

  car_type: carTypeSchema,

  license_plate: z
    .string()
    .min(1, 'Введите номерной знак')
    .max(10, 'Номерной знак должен содержать максимум 10 символов'),

  manufacture_year: z
    .number()
    .int('Год выпуска должен быть целым числом')
    .gte(1960, 'Год выпуска должен быть не меньше 1960')
    .lte(2026, 'Год выпуска должен быть не больше 2026'),

  photo: z.instanceof(File).optional(),

  VIN: z
    .string()
    .min(17, 'VIN код должен содержать 17 символов')
    .max(17, 'VIN код должен содержать 17 символов')
    .optional(),
})

export type CarFormOutput = z.output<typeof carSchema>

export type CarFormInput = {
  brand?: string
  model?: string
  cargo_capacity?: number
  volume_capacity?: number
  car_type?: CarType
  license_plate?: string
  manufacture_year?: number
  photo?: File
  VIN?: string
}
