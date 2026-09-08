import { apiRequest } from '@/lib/api'
import type { SupportTicket } from '@/types/index'

export type SupportRole = 'client' | 'executor'

export async function getSupportRequests(role: SupportRole) {
  return apiRequest<SupportTicket[]>(`/${role}/account/support/requests`)
}
