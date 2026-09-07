import { z } from 'zod'

export const profileSchema = z.object({
  name: z.string().min(1, 'Введите имя').max(20, 'Имя не должно превышать 20 символов'),

  phoneNumber: z.string().min(1, 'Введите номер телефона'),

  email: z.string().min(1, 'Введите email').email('Введите корректный email'),

  image: z.string().optional(),

  vinCode: z.string().max(17, 'VIN-код не должен превышать 17 символов').optional(),

  isNotificationsEnabled: z.boolean(),

  legalName: z.string().max(255, 'Название не должно превышать 255 символов').optional(),

  unp: z.string().max(50, 'УНП не должен превышать 50 символов').optional(),

  address: z.string().max(255, 'Адрес не должен превышать 255 символов').optional(),
})

export type ProfileFormInput = z.input<typeof profileSchema>
export type ProfileFormOutput = z.output<typeof profileSchema>
