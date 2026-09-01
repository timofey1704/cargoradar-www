import type { Executor } from '@/types/index'

export async function getCurrentExecutor(): Promise<Executor> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/executor/auth/me`, {
    method: 'GET',
    credentials: 'include',
  })

  if (response.status === 401) {
    throw new Error('UNAUTHORIZED')
  }

  if (!response.ok) {
    throw new Error('FAILED_TO_FETCH_EXECUTOR')
  }

  return response.json()
}
