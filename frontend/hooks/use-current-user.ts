'use client'

import { useQuery } from '@tanstack/react-query'
import { getCurrentClient } from '@/lib/auth/client'

export function useCurrentUser() {
  return useQuery({
    queryKey: ['current-client'],
    queryFn: getCurrentClient,
    retry: false,
    staleTime: 60 * 1000,
  })
}
