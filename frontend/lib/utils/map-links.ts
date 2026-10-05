import type { Coordinates } from '@/types/geo'

export function getGoogleMapsUrl(origin: Coordinates, destination: Coordinates) {
  const params = new URLSearchParams({
    api: '1',
    origin: `${origin.latitude},${origin.longitude}`,
    destination: `${destination.latitude},${destination.longitude}`,
    travelmode: 'driving',
  })
  return `https://www.google.com/maps/dir/?${params}`
}

export function getYandexMapsUrl(origin: Coordinates, destination: Coordinates) {
  const rtext = `${origin.latitude},${origin.longitude}~${destination.latitude},${destination.longitude}`
  return `https://yandex.by/maps/?${new URLSearchParams({ rtext, rtt: 'auto' })}`
}
