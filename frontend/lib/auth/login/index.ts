import type { LoginFormOutput } from '@/schemas/auth/login/loginSchema'

async function loginRequest(values: LoginFormOutput, url: string) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(values),
  })

  if (!response.ok) {
    throw new Error('Не удалось выполнить вход')
  }

  return response.json()
}

export async function clientLogin(values: LoginFormOutput) {
  return loginRequest(values, `${process.env.NEXT_PUBLIC_API_URL}/client/auth/login`)
}

export async function executorLogin(values: LoginFormOutput) {
  return loginRequest(values, `${process.env.NEXT_PUBLIC_API_URL}/executor/auth/login`)
}
