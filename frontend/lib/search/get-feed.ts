import type { Faq, SearchCardType } from '@/types'
const API_URL = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL

export async function getFeed(): Promise<SearchCardType[]> {
  const url = `${API_URL}/search/feed`

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
