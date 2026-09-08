import { apiRequest } from '@/lib/api'
import type { Executor } from '@/types'
import type { EditProfileFormOutput } from '@/schemas/executor/profile/profileSchema'

function toBackendPayload(values: EditProfileFormOutput) {
  const payload: Record<string, string | boolean | string[] | File | undefined> = {
    name: values.name,
    phone_number: values.phone_number,
    email: values.email,
    is_notifications_enabled: values.isNotificationsEnabled,
    image: values.image,
  }

  switch (values.type) {
    case 'carrier':
      break

    case 'supplier':
    case 'service':
      payload.legal_name = values.legal_name
      payload.UNP = values.UNP
      payload.address = values.address
      payload.brands = values.brands
      break
  }

  return payload
}

export async function changeAccountData(values: EditProfileFormOutput) {
  return apiRequest<Executor>('/executor/profile/update-data', {
    method: 'PATCH',
    body: toBackendPayload(values),
  })
}
