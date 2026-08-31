import { z } from 'zod'
import { belarusPhoneSchema } from '@/lib/validation/phone'

export const loginSchema = z.object({
  phone: belarusPhoneSchema,

  password: z
    .string()
    .min(1, 'Введите пароль')
    .min(8, 'Пароль должен содержать минимум 8 символов'),
})

// Тип для onSubmit (после transform)
export type LoginFormValues = z.output<typeof loginSchema>

// Тип для defaultValues и полей формы (до transform)
export type LoginFormInput = z.input<typeof loginSchema>