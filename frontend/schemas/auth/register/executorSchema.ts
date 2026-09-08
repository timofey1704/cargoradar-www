import { z } from 'zod'

import { belarusPhoneSchema } from '@/lib/validation/phone'
import { carSchema } from '@/schemas/car/carSchema'

export const ExecutorTypes = {
  carrier: 'carrier',
  supplier: 'supplier',
  service: 'service',
  towtruck: 'towtruck',
} as const

export const executorTypeSchema = z.enum(['carrier', 'supplier', 'service', 'towtruck'])

export type ExecutorType = z.infer<typeof executorTypeSchema>

export const ExecutorTypesNames: Record<ExecutorType, string> = {
  carrier: 'Перевозчик',
  supplier: 'Поставщик запчастей',
  service: 'СТО',
  towtruck: 'Эвакуатор',
}

const brandsSchema = z
  .array(z.string())
  .min(1, 'Выберите хотя бы одну марку автомобиля')
  .refine(value => !value.includes('all') || value.length === 1, {
    message: 'Нельзя выбрать «Все марки» вместе с конкретными марками',
  })

const commonFields = {
  name: z.string().min(1, 'Введите имя'),

  phone_number: belarusPhoneSchema,

  email: z.email('Введите корректный email'),

  password: z
    .string()
    .min(1, 'Введите пароль')
    .min(8, 'Пароль должен содержать минимум 8 символов'),

  privacy_accepted: z.literal(true, {
    error: 'Необходимо принять политику конфиденциальности',
  }),
}

export const carrierSchema = z.object({
  ...commonFields,

  type: z.literal('carrier'),

  cars: z.array(carSchema).min(1, 'Добавьте хотя бы один автомобиль'),
})

export const supplierSchema = z.object({
  ...commonFields,

  type: z.literal('supplier'),

  legal_name: z.string().min(1, 'Введите название юр. лица'),

  UNP: z
    .string()
    .min(9, 'УНП должен содержать 9 символов')
    .max(9, 'УНП должен содержать 9 символов'),

  pickup_point: z.string().min(1, 'Введите точку выдачи'),

  brands: brandsSchema,
})

export const serviceSchema = z.object({
  ...commonFields,

  type: z.literal('service'),

  legal_name: z.string().min(1, 'Введите название юр. лица'),

  UNP: z
    .string()
    .min(9, 'УНП должен содержать 9 символов')
    .max(9, 'УНП должен содержать 9 символов'),

  service_address: z.string().min(1, 'Введите адрес СТО'),

  brands: brandsSchema,
})

const towtruckSchema = z.object({
  ...commonFields,

  type: z.literal('towtruck'),
})

export const registerSchema = z.discriminatedUnion('type', [
  carrierSchema,
  supplierSchema,
  serviceSchema,
  towtruckSchema,
])

export type RegisterFormInput = z.input<typeof registerSchema>
export type RegisterFormOutput = z.output<typeof registerSchema>
