import { useQuery } from '@tanstack/react-query'

import { getMembershipInfo } from '@/lib/utils/membership'
import type { MembershipInfo } from '@/types/index'

type MembershipRole = 'client' | 'executor'

export function useGetMembershipInfo(role: MembershipRole = 'client') {
  return useQuery<MembershipInfo>({
    queryKey: ['membership-info', role],
    queryFn: () => getMembershipInfo(role),
    retry: false,
  })
}
