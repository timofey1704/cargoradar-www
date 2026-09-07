import { apiRequest } from '@/lib/api'
import type { SupportTicket } from '@/types/index'

export async function clientRequest() {
  return apiRequest<SupportTicket[]>('/client/account/support/requests')
}

export async function executorRequest() {
  return apiRequest<SupportTicket[]>('/executor/account/support/requests')
}
