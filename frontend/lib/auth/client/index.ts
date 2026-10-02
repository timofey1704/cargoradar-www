import type { Client } from '@/types/index'
import { apiRequest } from '@/lib/api'

export async function getCurrentClient(): Promise<Client> {
  return apiRequest<Client>('/client/auth/me')
}
