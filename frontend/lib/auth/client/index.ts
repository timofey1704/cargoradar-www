import type { Client } from '@/types/index'

export async function getCurrentClient(): Promise<Client> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/client/auth/me`, {
    method: 'GET',
    credentials: 'include',
  })

  if (response.status === 401) {
    throw new Error('UNAUTHORIZED')
  }

  if (!response.ok) {
    throw new Error('FAILED_TO_FETCH_USER')
  }

  return response.json()
}
