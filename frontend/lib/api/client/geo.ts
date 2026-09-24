import { apiRequest } from '@/lib/api'

import type { GeoReverseResult, GeoSearchResult, RouteData } from '@/types/geo'

interface SearchGeoParams {
  query: string
  limit?: number
}

interface ReverseGeoParams {
  latitude: number
  longitude: number
}

interface GetRouteParams {
  origin: {
    latitude: number
    longitude: number
  }

  destination: {
    latitude: number
    longitude: number
  }
}

export const searchGeo = ({ query, limit = 5 }: SearchGeoParams) => {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  })

  return apiRequest<GeoSearchResult[]>(`/geo/search?${params.toString()}`)
}

export const reverseGeo = ({ latitude, longitude }: ReverseGeoParams) => {
  const params = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
  })

  return apiRequest<GeoReverseResult>(`/geo/reverse?${params.toString()}`)
}

export const getRoute = ({ origin, destination }: GetRouteParams) => {
  const params = new URLSearchParams({
    origin_latitude: String(origin.latitude),
    origin_longitude: String(origin.longitude),
    destination_latitude: String(destination.latitude),
    destination_longitude: String(destination.longitude),
  })

  return apiRequest<RouteData>(`/geo/route?${params.toString()}`)
}
