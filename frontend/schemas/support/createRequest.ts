import { z } from 'zod'

export const supportSchema = z.object({
  requestType: z.string().min(1, 'Выберите тип обращения'),

  title: z
    .string()
    .min(1, 'Введите тему обращения')
    .max(255, 'Тема не должна превышать 255 символов'),

  description: z
    .string()
    .min(1, 'Опишите проблему')
    .max(5000, 'Описание не должно превышать 5000 символов'),
})

export type SupportFormInput = z.input<typeof supportSchema>
export type SupportFormOutput = z.output<typeof supportSchema>
