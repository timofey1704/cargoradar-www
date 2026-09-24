import { apiRequest } from '@/lib/api'
import type { Client } from '@/types'
import type { ProfileFormOutput } from '@/schemas/account/profileSchema'

function toBackendPayload(values: ProfileFormOutput) {
  const payload: Record<string, string | boolean | undefined> = {
    name: values.name,
    phone_number: values.phoneNumber,
    email: values.email,
    is_notifications_enabled: values.isNotificationsEnabled,
  }

  if (values.vinCode) {
    payload.VIN_code = values.vinCode
  }

  // Юрданные шлём только если хоть одно из них заполнено —
  // пустые строки на бэке равносильны "не передавали".
  if (values.legalName || values.unp || values.address) {
    payload.legal_name = values.legalName
    payload.unp = values.unp
    payload.address = values.address
  }

  return payload
}

export async function changeAccountData(values: ProfileFormOutput) {
  return apiRequest<Client>('/client/profile/update-data', {
    method: 'PATCH',
    body: toBackendPayload(values),
  })
}
