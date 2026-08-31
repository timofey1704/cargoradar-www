import type { LoginFormOutput } from '@/schemas/auth/login/loginSchema'

export async function client_login(values: LoginFormOutput) {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/client/auth/login`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    },
  )

  if (!response.ok) {
    throw new Error('Не удалось выполнить вход')
  }

  return response.json()
}