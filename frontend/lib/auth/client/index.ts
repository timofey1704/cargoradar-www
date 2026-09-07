import type { Client } from '@/types/index'

export async function getCurrentClient(): Promise<Client> {
  const url = `${process.env.NEXT_PUBLIC_API_URL}/client/auth/me`

  // console.log('[auth:me] GET', url, '| document.cookie =', document.cookie)

  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include',
  })

  // console.log(
  //   '[auth:me] status =',
  //   response.status,
  //   '| cookies now =',
  //   document.cookie,
  // )

  if (response.status === 401) {
    console.warn('[auth:me] 401 UNAUTHORIZED')
    throw new Error('UNAUTHORIZED')
  }

  if (!response.ok) {
    console.warn('[auth:me] non-ok status', response.status)
    throw new Error('FAILED_TO_FETCH_USER')
  }

  const json = await response.json()
  // console.log('[auth:me] ok, body keys =', Object.keys(json))

  return json
}
