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

/**
 * Схема состояния автомобиля внутри формы.
 *
 * Все поля, которые пользователь должен заполнить,
 * могут быть undefined до момента заполнения.
 */
const carFormSchema = carSchema.partial()

export const registerSchema = z
  .object({
    name: z.string().min(1, 'Введите имя'),

    phone_number: belarusPhoneSchema,

    email: z.email('Введите корректный email'),

    password: z
      .string()
      .min(1, 'Введите пароль')
      .min(8, 'Пароль должен содержать минимум 8 символов'),

    type: executorTypeSchema,

    cars: z.array(carFormSchema).optional(),

    privacy_accepted: z.literal(true, {
      error: 'Необходимо принять политику конфиденциальности',
    }),
  })
  .superRefine((data, ctx) => {
    // для перевозчика автомобиль обязателен
    if (data.type === 'carrier') {
      if (!data.cars?.length) {
        ctx.addIssue({
          code: 'custom',
          path: ['cars'],
          message: 'Добавьте хотя бы один автомобиль',
        })

        return
      }

      // каждый автомобиль должен соответствовать полноценной carSchema
      data.cars.forEach((car, index) => {
        const result = carSchema.safeParse(car)

        if (!result.success) {
          result.error.issues.forEach(issue => {
            ctx.addIssue({
              ...issue,
              path: ['cars', index, ...issue.path],
            })
          })
        }
      })
    }
  })

export type RegisterFormInput = z.input<typeof registerSchema>
export type RegisterFormOutput = z.output<typeof registerSchema>
