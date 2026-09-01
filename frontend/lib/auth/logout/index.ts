async function logoutRequest(url: string) {
  const response = await fetch(url, {
    method: 'POST',
    credentials: 'include',
  })

  if (!response.ok) {
    throw new Error('Не удалось выполнить выход')
  }
}

export async function clientLogout() {
  return logoutRequest(`${process.env.NEXT_PUBLIC_API_URL}/client/auth/logout`)
}

export async function executorLogout() {
  return logoutRequest(`${process.env.NEXT_PUBLIC_API_URL}/executor/auth/logout`)
}
