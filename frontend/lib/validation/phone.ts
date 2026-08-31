import { z } from 'zod'
import { parsePhoneNumberFromString } from 'libphonenumber-js'

export const belarusPhoneSchema = z
  .string()
  .min(1, 'Введите номер телефона')
  .refine(
    (value) => value.trim().startsWith('+375'),
    'Номер должен начинаться с +375',
  )
  .transform((value, ctx) => {
    const phone = parsePhoneNumberFromString(value, 'BY')

    if (!phone || !phone.isValid() || phone.country !== 'BY') {
      ctx.addIssue({
        code: 'custom',
        message: 'Введите корректный номер телефона',
      })

      return z.NEVER
    }

    return phone.number
  })