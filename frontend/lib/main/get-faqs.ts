import type { Faq } from '@/types'
const API_URL = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL

export async function getFaq(): Promise<Faq[]> {
  const url = `${API_URL}/main/faq`

  try {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      cache: 'no-store',
    })

    if (!response.ok) {
      console.warn('[faq] non-ok status', response.status)
      return []
    }

    const json = await response.json()
    return Array.isArray(json) ? json : []
  } catch (error) {
    console.warn('[faq] failed to fetch', error)
    return []
  }
}
