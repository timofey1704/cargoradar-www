import { z } from 'zod'

import {
  carrierSchema,
  supplierSchema,
  serviceSchema,
} from '@/schemas/auth/register/executorSchema'

const editableFields = {
  image: z.instanceof(File).optional().or(z.string().optional()),

  isNotificationsEnabled: z.boolean(),
}

export const editProfileSchema = z.discriminatedUnion('type', [
  carrierSchema.omit({ password: true, privacy_accepted: true, cars: true }).extend(editableFields),
  supplierSchema.omit({ password: true, privacy_accepted: true }).extend(editableFields),
  serviceSchema.omit({ password: true, privacy_accepted: true }).extend(editableFields),
])

export type EditProfileFormInput = z.input<typeof editProfileSchema>
export type EditProfileFormOutput = z.output<typeof editProfileSchema>
