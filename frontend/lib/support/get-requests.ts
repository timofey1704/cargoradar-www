import type { SupportTicket } from '@/types/index'

async function getClientRequests(user_id: number, url: string): Promise<SupportTicket> {
  console.log('[support:request] GET', url)

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
  })
  console.log('[support:request] status =', response.status, 'ok =', response.ok)

  if (response.status === 401) {
    console.warn('[support:get] 401 UNAUTHORIZED')
    throw new Error('UNAUTHORIZED')
  }

  if (!response.ok) {
    console.warn('[support:get] non-ok status', response.status)
    throw new Error('FAILED_TO_FETCH_USER')
  }

  const json = await response.json()
  console.log('[support:get] ok, body keys =', Object.keys(json))

  return json
}

export async function clientRequest(user_id: number) {
  return getClientRequests(user_id, `${process.env.NEXT_PUBLIC_API_URL}/client/support/requests`)
}

export async function executorRequest(user_id: number) {
  return getClientRequests(user_id, `${process.env.NEXT_PUBLIC_API_URL}/executor/support/requests`)
}
