'use client'

import { useEffect, useMemo, useState } from 'react'

import { CircleMarker, MapContainer, Polyline, TileLayer, useMap } from 'react-leaflet'

import type { LatLngBoundsExpression } from 'leaflet'

import { getRoute } from '@/lib/api/client/geo'

import type { Coordinates, RouteData } from '@/types/geo'

interface RouteMapProps {
  origin: Coordinates | null
  destination: Coordinates | null
}

interface MapViewportProps {
  origin: Coordinates
  destination: Coordinates
}

function MapViewport({ origin, destination }: MapViewportProps) {
  const map = useMap()

  useEffect(() => {
    const bounds: LatLngBoundsExpression = [
      [origin.latitude, origin.longitude],
      [destination.latitude, destination.longitude],
    ]

    map.fitBounds(bounds, {
      padding: [40, 40],
      maxZoom: 13,
    })
  }, [map, origin, destination])

  return null
}

export function RouteMap({ origin, destination }: RouteMapProps) {
  const [route, setRoute] = useState<RouteData | null>(null)

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!origin || !destination) {
      setRoute(null)
      setError(null)
      return
    }

    let cancelled = false

    const loadRoute = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const data = await getRoute({
          origin,
          destination,
        })

        if (!cancelled) {
          setRoute(data)
        }
      } catch {
        if (!cancelled) {
          setRoute(null)
          setError('Не удалось построить маршрут')
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    loadRoute()

    return () => {
      cancelled = true
    }
  }, [origin, destination])

  const center = useMemo(() => {
    if (origin) {
      return [origin.latitude, origin.longitude] as [number, number]
    }

    return [53.9023, 27.5619] as [number, number]
  }, [origin])

  const hasRoute = Boolean(origin) && Boolean(destination)

  return (
    <div className="relative overflow-hidden rounded-2xl border border-gray-200 bg-gray-100">
      <div className="h-100">
        <MapContainer center={center} zoom={12} className="h-full w-full" scrollWheelZoom>
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {origin && destination && (
            <>
              <CircleMarker
                center={[origin.latitude, origin.longitude]}
                radius={8}
                pathOptions={{
                  color: '#ff6731',
                  fillColor: '#ff6731',
                  fillOpacity: 1,
                }}
              />

              <CircleMarker
                center={[destination.latitude, destination.longitude]}
                radius={8}
                pathOptions={{
                  color: '#1c1c29',
                  fillColor: '#1c1c29',
                  fillOpacity: 1,
                }}
              />

              {route && (
                <Polyline
                  positions={route.geometry}
                  pathOptions={{
                    color: '#ff6731',
                    weight: 5,
                    opacity: 0.8,
                  }}
                />
              )}

              <MapViewport origin={origin} destination={destination} />
            </>
          )}
        </MapContainer>
      </div>

      {!hasRoute && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/40 backdrop-blur-[1px]">
          <div className="rounded-xl bg-white px-5 py-4 text-center shadow-lg">
            <p className="text-sm font-medium text-gray-800">
              Укажите точки отправления и назначения
            </p>

            <p className="mt-1 text-xs text-gray-500">Маршрут появится после выбора обеих точек</p>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="absolute top-4 left-1/2 z-20 -translate-x-1/2 rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-lg">
          Строим маршрут...
        </div>
      )}

      {error && (
        <div className="absolute bottom-4 left-1/2 z-20 -translate-x-1/2 rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-red-500 shadow-lg">
          {error}
        </div>
      )}

      {route && (
        <div className="absolute right-4 bottom-4 left-4 z-20 flex items-center justify-center gap-6 rounded-xl bg-white/95 px-4 py-3 shadow-lg backdrop-blur-sm">
          <div>
            <p className="text-xs text-gray-500">Расстояние</p>

            <p className="text-sm font-semibold text-gray-900">
              {route.distanceKm.toLocaleString('ru-RU', {
                maximumFractionDigits: 1,
              })}{' '}
              км
            </p>
          </div>

          <div className="h-8 w-px bg-gray-200" />

          <div>
            <p className="text-xs text-gray-500">Время в пути</p>

            <p className="text-sm font-semibold text-gray-900">
              {formatDuration(route.durationMinutes)}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

function formatDuration(minutes: number) {
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = Math.round(minutes % 60)

  if (hours === 0) {
    return `${remainingMinutes} мин`
  }

  if (remainingMinutes === 0) {
    return `${hours} ч`
  }

  return `${hours} ч ${remainingMinutes} мин`
}
