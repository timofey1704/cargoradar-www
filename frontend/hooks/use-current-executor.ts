'use client'

import { useQuery } from '@tanstack/react-query'
import { getCurrentExecutor } from '@/lib/auth/executor'

export function useCurrentExecutor() {
  return useQuery({
    queryKey: ['current-executor'],
    queryFn: getCurrentExecutor,
    retry: false,
    staleTime: 60 * 1000,
  })
}
