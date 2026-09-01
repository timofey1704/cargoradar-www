import { z } from 'zod'
import { belarusPhoneSchema } from '@/lib/validation/phone'
import { carSchema as carSchema } from '@/schemas/car/carSchema'

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

export const registerSchema = z.object({
  name: z.string().min(1, 'Введите имя'),
  phone_number: belarusPhoneSchema,
  email: z.email('Введите корректный email'),
  password: z
    .string()
    .min(1, 'Введите пароль')
    .min(8, 'Пароль должен содержать минимум 8 символов'),
  type: executorTypeSchema,
  car: carSchema.optional(),
  privacy_accepted: z.literal(true, {
    error: 'Необходимо принять политику конфиденциальности',
  }),
})

export type RegisterFormInput = z.input<typeof registerSchema>
export type RegisterFormOutput = z.output<typeof registerSchema>
