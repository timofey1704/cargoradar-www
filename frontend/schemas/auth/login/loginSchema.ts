import { z } from 'zod'
import { belarusPhoneSchema } from '@/lib/validation/phone'

export const loginSchema = z.object({
  phone_number: belarusPhoneSchema,

  password: z
    .string()
    .min(1, 'Введите пароль')
    .min(8, 'Пароль должен содержать минимум 8 символов'),
})

export type LoginFormInput = z.input<typeof loginSchema>
export type LoginFormOutput = z.output<typeof loginSchema>