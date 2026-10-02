import type { Executor } from '@/types/index'
import { apiRequest } from '@/lib/api'

export async function getCurrentExecutor(): Promise<Executor> {
  return apiRequest<Executor>('/executor/auth/me')
}
