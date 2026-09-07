import type { SupportFormOutput } from '@/schemas/support/createRequest'

async function createSupportRequest(values: SupportFormOutput, url: string) {
  console.log('[support:request] POST', url)

  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })

  console.log('[support:request] status =', response.status, 'ok =', response.ok)

  if (!response.ok) {
    throw new Error('Не удалось выполнить вход')
  }

  const json = await response.json()

  console.log('[support:request] body keys =', Object.keys(json))

  return json
}

export async function clientRequest(values: SupportFormOutput) {
  return createSupportRequest(
    values,
    `${process.env.NEXT_PUBLIC_API_URL}/client/account/support/create-request`
  )
}

export async function executorRequest(values: SupportFormOutput) {
  return createSupportRequest(
    values,
    `${process.env.NEXT_PUBLIC_API_URL}/executor/account/support/create-request`
  )
}
