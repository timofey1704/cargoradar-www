import { z } from 'zod'

const coordinatesSchema = z.object({
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
})

const routePointSchema = z
  .object({
    address: z.string().min(1, 'Укажите адрес'),

    location: coordinatesSchema.nullable(),
  })
  .superRefine((value, ctx) => {
    if (!value.location) {
      ctx.addIssue({
        code: 'custom',
        path: ['location'],
        message: 'Выберите точку на карте',
      })
    }
  })

export const createOrderSchema = z.object({
  origin: routePointSchema,

  destination: routePointSchema,

  cargo_type: z.string().min(1, 'Укажите тип груза').max(100),

  weight_kg: z.preprocess(
    value => {
      if (value === '' || value === undefined || Number.isNaN(value)) {
        return undefined
      }

      return value
    },
    z
      .number({
        error: 'Укажите вес груза',
      })
      .positive('Вес должен быть больше 0')
  ),

  volume_m3: z.number().positive('Объём должен быть больше 0').nullable(),

  vehicle_type: z.string().max(100).nullable(),

  loading_date: z.string().min(1, 'Укажите дату загрузки'),

  budget: z.number().min(0, 'Бюджет не может быть отрицательным').nullable(),

  comment: z.string().nullable(),
})

export type CreateOrderFormValues = z.infer<typeof createOrderSchema>
