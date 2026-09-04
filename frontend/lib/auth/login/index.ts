import type { LoginFormOutput } from '@/schemas/auth/login/loginSchema'

async function loginRequest(values: LoginFormOutput, url: string) {
  console.log('[auth:login] POST', url)

  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })

  console.log('[auth:login] status =', response.status, 'ok =', response.ok)

  if (!response.ok) {
    throw new Error('Не удалось выполнить вход')
  }

  const json = await response.json()

  console.log('[auth:login] body keys =', Object.keys(json))

  return json
}

export async function clientLogin(values: LoginFormOutput) {
  return loginRequest(values, `${process.env.NEXT_PUBLIC_API_URL}/client/auth/login`)
}

export async function executorLogin(values: LoginFormOutput) {
  return loginRequest(values, `${process.env.NEXT_PUBLIC_API_URL}/executor/auth/login`)
}
