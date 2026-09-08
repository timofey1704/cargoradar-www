import { apiRequest } from '@/lib/api'
import type { MembershipInfo } from '@/types/index'

export async function getMembershipInfo() {
  return apiRequest<MembershipInfo>('/client/membership/info')
}

export async function getExecutorMembershipInfo() {
  return apiRequest<MembershipInfo>('/executor/membership/info')
}
