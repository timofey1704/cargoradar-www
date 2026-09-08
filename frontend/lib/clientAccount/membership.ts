import { apiRequest } from '@/lib/api'
import type { MembershipInfo } from '@/types/index'

type MembershipRole = 'client' | 'executor'

export async function getMembershipInfo(role: MembershipRole = 'client') {
  return apiRequest<MembershipInfo>(`/${role}/membership/info`)
}
