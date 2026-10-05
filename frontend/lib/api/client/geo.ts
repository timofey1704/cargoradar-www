import { apiRequest } from '@/lib/api'

import type { GeoReverseResult, GeoSearchResult, RouteData } from '@/types/geo'

interface SearchGeoParams {
  query: string
  limit?: number
  signal?: AbortSignal
}

interface SearchGeoResponse {
  place_id: string
  display_name: string
  latitude: number
  longitude: number
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

interface GetRouteResponse {
  distance_km: number
  duration_minutes: number
  geometry: [number, number][]
}

export const searchGeo = async ({ query, limit = 5, signal }: SearchGeoParams) => {
  const params = new URLSearchParams({
    q: query,
    limit: String(limit),
  })

  const results = await apiRequest<SearchGeoResponse[]>(`/geo/search?${params.toString()}`, {
    signal,
  })

  return results.map(({ place_id, display_name, latitude, longitude }): GeoSearchResult => ({
    placeId: place_id,
    displayName: display_name,
    latitude,
    longitude,
  }))
}

export const reverseGeo = ({ latitude, longitude }: ReverseGeoParams) => {
  const params = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
  })

  return apiRequest<GeoReverseResult>(`/geo/reverse?${params.toString()}`)
}

export const getRoute = async ({ origin, destination }: GetRouteParams) => {
  const params = new URLSearchParams({
    origin_latitude: String(origin.latitude),
    origin_longitude: String(origin.longitude),
    destination_latitude: String(destination.latitude),
    destination_longitude: String(destination.longitude),
  })

  const response = await apiRequest<GetRouteResponse>(`/geo/route?${params.toString()}`)

  if (
    !Number.isFinite(response.distance_km) ||
    !Number.isFinite(response.duration_minutes) ||
    !Array.isArray(response.geometry)
  ) {
    throw new Error('Некорректный ответ сервера маршрутов')
  }

  const route: RouteData = {
    distanceKm: response.distance_km,
    durationMinutes: response.duration_minutes,
    geometry: response.geometry,
  }

  return route
}
