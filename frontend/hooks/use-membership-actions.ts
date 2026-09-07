import { useQuery } from '@tanstack/react-query'

import { getMembershipInfo } from '@/lib/clientAccount/membership'
import type { MembershipInfo } from '@/types/index'

export function useGetMembershipInfo() {
  return useQuery<MembershipInfo>({
    queryKey: ['membership-info'],
    queryFn: getMembershipInfo,
    retry: false,
  })
}
