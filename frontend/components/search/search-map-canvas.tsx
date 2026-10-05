'use client'

import { useEffect } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import type { LatLngBoundsExpression } from 'leaflet'

import type { SearchMapMarker } from './search-map'
import { deselectFeedItem, selectFeedItem } from './search-feed-events'
import { RequestOfferAction } from './request-offer-action'

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
    <div className="relative h-112 overflow-hidden rounded-xl border border-gray-200 bg-gray-100 lg:h-[calc(100svh-6rem)] lg:min-h-0">
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
              eventHandlers={{
                popupopen: () => selectFeedItem(point.itemId),
                popupclose: () => deselectFeedItem(),
              }}
            >
              <Popup minWidth={240}>
                <div className="min-w-52 space-y-3">
                  <span className="bg-orange/10 text-orange inline-flex rounded-full px-2.5 py-1 text-xs font-semibold tracking-[0.08em] uppercase">
                    {point.kind}
                  </span>

                  {(point.from || point.to) && (
                    <div className="space-y-1.5 rounded-xl bg-gray-50 p-3 text-sm">
                      {point.from && (
                        <p className="flex gap-2">
                          <span className="w-14 shrink-0 text-xs text-gray-400">Откуда</span>
                          <span className="text-text min-w-0 text-sm font-semibold">
                            {point.from}
                          </span>
                        </p>
                      )}
                      {point.to && (
                        <p className="flex gap-2">
                          <span className="w-14 shrink-0 text-xs text-gray-400">Куда</span>
                          <span className="text-text min-w-0 text-sm font-semibold">
                            {point.to}
                          </span>
                        </p>
                      )}
                    </div>
                  )}

                  {point.price !== null && point.price !== undefined && (
                    <p className="text-text text-sm font-semibold">
                      {point.priceLabel ?? 'Цена'}: {point.price.toLocaleString('ru-RU')} BYN
                    </p>
                  )}

                  {point.feedItem.kind === 'request' && (
                    <RequestOfferAction item={point.feedItem} />
                  )}
                </div>
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
