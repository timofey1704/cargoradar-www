export type SearchFeedKind = 'route' | 'post' | 'request'

export type SearchCategoryKey = 'carriers' | 'suppliers' | 'service-stations' | 'tow-trucks'

export interface SearchRoutePayload {
  id: number
  executor_id: number
  point_a: string
  point_b: string
  distance_km: number | null
  duration_min: number | null
  comment: string | null
  price: number | null
  created_at: string
}

export interface SearchPostPayload {
  id: number
  creator_type: 'client' | 'executor'
  client_id: number | null
  executor_id: number | null
  title: string
  request_text: string
  created_at: string
}

export interface SearchRequestPayload {
  id: number
  client_id: number
  status: string
  origin_address: string
  destination_address: string
  cargo_type: string
  weight_kg: number
  volume_m3: number | null
  vehicle_type: string | null
  loading_date: string
  budget: number | null
  comment: string | null
  created_at: string
}

export type SearchFeedItem =
  | {
      kind: 'route'
      id: number
      created_at: string
      route: SearchRoutePayload | null
      post: null
    }
  | {
      kind: 'post'
      id: number
      created_at: string
      route: null
      post: SearchPostPayload | null
    }
  | {
      kind: 'request'
      id: number
      created_at: string
      route: null
      post: null
      request: SearchRequestPayload | null
    }

export interface SearchFeedPage {
  items: SearchFeedItem[]
  total: number
  skip: number
  limit: number
  has_more: boolean
}

const API_URL = process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL

export async function getFeed(): Promise<SearchFeedPage> {
  const url = `${API_URL}/search/feed`

  try {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      cache: 'no-store',
    })

    if (!response.ok) {
      console.warn('[search-feed] non-ok status', response.status)
      return { items: [], total: 0, skip: 0, limit: 20, has_more: false }
    }

    const json = await response.json()

    if (!json || typeof json !== 'object' || !Array.isArray((json as SearchFeedPage).items)) {
      return { items: [], total: 0, skip: 0, limit: 20, has_more: false }
    }

    return json as SearchFeedPage
  } catch (error) {
    console.warn('[search-feed] failed to fetch', error)
    return { items: [], total: 0, skip: 0, limit: 20, has_more: false }
  }
}

export function getCategoryItems(
  items: SearchFeedItem[],
  category: SearchCategoryKey
): SearchFeedItem[] {
  switch (category) {
    case 'carriers':
      return items.filter(item => item.kind === 'route')
    case 'suppliers':
    case 'service-stations':
    case 'tow-trucks':
      return items.filter(item => item.kind === 'post')
    default:
      return items
  }
}
