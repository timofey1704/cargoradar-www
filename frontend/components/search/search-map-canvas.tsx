'use client'

import { useEffect } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import type { LatLngBoundsExpression } from 'leaflet'

import type { SearchMapMarker } from './search-map'

const DEFAULT_CENTER: [number, number] = [53.9023, 27.5619]

function MapViewport({ points }: { points: SearchMapMarker[] }) {
  const map = useMap()

  useEffect(() => {
    if (!points.length) {
      map.setView(DEFAULT_CENTER, 7)
      return
    }

    const bounds: LatLngBoundsExpression = points.map(
      point => [point.latitude, point.longitude] as [number, number]
    )

    if (bounds.length === 1) {
      map.setView(bounds[0] as [number, number], 12)
      return
    }

    map.fitBounds(bounds, { padding: [36, 36], maxZoom: 12 })
  }, [map, points])

  return null
}

export function SearchMapCanvas({ points }: { points: SearchMapMarker[] }) {
  return (
    <div className="relative h-112 overflow-hidden rounded-xl border border-gray-200 bg-gray-100 lg:h-[calc(100vh-8rem)] lg:min-h-136">
      <MapContainer center={DEFAULT_CENTER} zoom={7} className="h-full w-full" scrollWheelZoom>
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapViewport points={points} />

        {points.map(point => {
          const color = point.kind === 'Маршрут водителя' ? '#292b2e' : '#ed6333'

          return (
            <CircleMarker
              key={point.id}
              center={[point.latitude, point.longitude]}
              radius={8}
              pathOptions={{ color, fillColor: color, fillOpacity: 0.9, weight: 2 }}
            >
              <Popup>
                <strong>{point.kind}</strong>
                <br />
                {point.label}
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>

      {!points.length && (
        <div className="pointer-events-none absolute inset-x-4 bottom-4 rounded-lg bg-white/95 px-4 py-3 text-center text-sm text-gray-600 shadow">
          У результатов пока нет координат
        </div>
      )}
    </div>
  )
}
