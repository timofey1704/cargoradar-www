import type { LoginFormOutput } from '@/schemas/auth/login/loginSchema'

async function login_request(values: LoginFormOutput, url: string) {
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

export async function client_login(values: LoginFormOutput) {
  return login_request(values, `${process.env.NEXT_PUBLIC_API_URL}/client/auth/login`)
}

export async function executor_login(values: LoginFormOutput) {
  return login_request(values, `${process.env.NEXT_PUBLIC_API_URL}/client/executor/login`)
}
