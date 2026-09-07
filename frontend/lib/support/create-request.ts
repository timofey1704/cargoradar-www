import { apiRequest } from '@/lib/api'
import type { SupportFormOutput } from '@/schemas/support/createRequest'

// Поля формы — camelCase (requestType), бэкенд ждёт snake_case (request_type).
function toBackendPayload(values: SupportFormOutput) {
  return {
    request_type: values.requestType,
    title: values.title,
    description: values.description,
  }
}

export async function clientRequest(values: SupportFormOutput) {
  return apiRequest('/client/account/support/create-request', {
    method: 'POST',
    body: toBackendPayload(values),
  })
}

export async function executorRequest(values: SupportFormOutput) {
  return apiRequest('/executor/account/support/create-request', {
    method: 'POST',
    body: toBackendPayload(values),
  })
}
