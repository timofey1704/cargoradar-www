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
  brand: z.string().min(1, 'Введите марку автомобиля'),
  model: z.string().min(1, 'Введите модель автомобиля'),
  cargo_capacity: z.number().int().gt(0, 'Грузоподъёмность должна быть больше 0'),
  volume_capacity: z.number().int().gt(0, 'Объём должен быть больше 0').optional(),
  car_type: carTypeSchema,
  license_plate: z
    .string()
    .min(1, 'Введите номерной знак')
    .max(10, 'Номерной знак должен содержать максимум 10 символов'),
  manufacture_year: z
    .number()
    .int()
    .gte(1960, 'Год выпуска должен быть не меньше 1960')
    .lte(2026, 'Год выпуска должен быть не больше 2026'),
  photo_url: z
    .string()
    .max(255, 'URL фотографии должен содержать максимум 255 символов')
    .optional(),
  VIN: z
    .string()
    .min(17, 'Введите VIN код')
    .max(17, 'VIN код должен содержать максимум 17 символов')
    .optional(),
})

export type CarFormInput = z.input<typeof carSchema>
export type CarFormOutput = z.output<typeof carSchema>
export type CarType = z.infer<typeof carTypeSchema>
