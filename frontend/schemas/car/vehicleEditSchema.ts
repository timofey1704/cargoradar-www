import { z } from 'zod'

export const vehicleEditSchema = z.object({
  cargo_capacity: z.number().int().gt(0, 'Укажите грузоподъёмность больше 0'),
  volume_capacity: z.number().int().gt(0, 'Объём должен быть больше 0').nullable(),
  license_plate: z
    .string()
    .min(1, 'Введите номерной знак')
    .max(10, 'Номерной знак должен содержать максимум 10 символов'),
})

export type VehicleEditValues = z.infer<typeof vehicleEditSchema>
