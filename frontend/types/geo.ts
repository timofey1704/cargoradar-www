export interface Coordinates {
  latitude: number
  longitude: number
}

export interface RoutePointValue {
  address: string
  location: Coordinates | null
}

export interface GeoSearchResult {
  placeId: string
  displayName: string
  latitude: number
  longitude: number
}

export interface GeoReverseResult {
  address: string
  latitude: number
  longitude: number
}

export interface Coordinates {
  latitude: number
  longitude: number
}

export interface RouteData {
  distanceKm: number
  durationMinutes: number

  // Leaflet: [latitude, longitude]
  geometry: [number, number][]
}
