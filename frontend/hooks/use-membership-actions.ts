import { useQuery } from '@tanstack/react-query'

import { getMembershipInfo, getExecutorMembershipInfo } from '@/lib/clientAccount/membership'
import type { MembershipInfo } from '@/types/index'

export function useGetMembershipInfo() {
  return useQuery<MembershipInfo>({
    queryKey: ['membership-info'],
    queryFn: getMembershipInfo,
    retry: false,
  })
}

export function useGetExecutorMembershipInfo() {
  return useQuery<MembershipInfo>({
    queryKey: ['executor-membership-info'],
    queryFn: getExecutorMembershipInfo,
    retry: false,
  })
}
