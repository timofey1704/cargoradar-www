import { z } from 'zod'

import { belarusPhoneSchema } from '@/lib/validation/phone'

export const ClientTypes = {
  individual: 'individual',
  legal: 'legal',
} as const

export const clientTypeSchema = z.enum(['individual', 'legal'])

export type ClientType = z.infer<typeof clientTypeSchema>

export const ClientTypesNames: Record<ClientType, string> = {
  individual: 'Физическое лицо',
  legal: 'Юридическое лицо',
}

const commonFields = {
  name: z.string().min(1, 'Введите имя'),

  phone_number: belarusPhoneSchema,

  email: z.email('Введите корректный email'),

  password: z
    .string()
    .min(1, 'Введите пароль')
    .min(8, 'Пароль должен содержать минимум 8 символов'),

  VIN_code: z.string().length(17, 'VIN код должен содержать 17 символов').optional(),

  privacy_accepted: z.literal(true, {
    error: 'Необходимо принять политику конфиденциальности',
  }),
}

const individualSchema = z.object({
  ...commonFields,

  type: z.literal('individual'),
})

const legalSchema = z.object({
  ...commonFields,

  type: z.literal('legal'),

  legal_name: z.string().min(1, 'Введите название юр. лица'),

  UNP: z
    .string()
    .min(9, 'УНП должен содержать 9 символов')
    .max(9, 'УНП должен содержать 9 символов'),

  address: z.string().min(1, 'Введите адрес'),
})

export const registerSchema = z.discriminatedUnion('type', [individualSchema, legalSchema])

export type RegisterFormInput = z.input<typeof registerSchema>
export type RegisterFormOutput = z.output<typeof registerSchema>
