import { z } from 'zod'
import { belarusPhoneSchema } from '@/lib/validation/phone'

export const registerSchema = z.object({
  name: z.string().min(1, 'Введите имя'),
  phone: belarusPhoneSchema,
  email: z.email('Введите корректный email'),
  password: z
    .string()
    .min(1, 'Введите пароль')
    .min(8, 'Пароль должен содержать минимум 8 символов'),
  VIN_code: z.string().length(17, 'VIN код должен содержать 17 символов').optional(),
  privacyAccepted: z.literal(true, {
    error: 'Необходимо принять политику конфиденциальности',
  }),
})

export type RegisterFormInput = z.input<typeof registerSchema>
export type RegisterFormOutput = z.output<typeof registerSchema>
