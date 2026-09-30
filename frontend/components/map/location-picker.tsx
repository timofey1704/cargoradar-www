'use client'

import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet'
import { type LatLngExpression } from 'leaflet'

import { MapMarker } from './map-marker'
import { markerIcon } from './map-icons'

import type { Coordinates } from '@/types/geo'

interface LocationPickerProps {
  value: Coordinates | null
  onChange: (value: Coordinates) => void
}

const DEFAULT_CENTER: LatLngExpression = [53.9023, 27.5619]

const DEFAULT_ZOOM = 12

interface MapClickHandlerProps {
  onChange: (value: Coordinates) => void
}

function MapClickHandler({ onChange }: MapClickHandlerProps) {
  useMapEvents({
    click(event) {
      onChange({
        latitude: event.latlng.lat,
        longitude: event.latlng.lng,
      })
    },
  })

  return null
}

export function LocationPicker({ value, onChange }: LocationPickerProps) {
  const [center, setCenter] = useState<LatLngExpression>(DEFAULT_CENTER)

  useEffect(() => {
    if (!value) {
      return
    }

    setCenter([value.latitude, value.longitude])
  }, [value])

  const markerPosition = useMemo<LatLngExpression | null>(() => {
    if (!value) {
      return null
    }

    return [value.latitude, value.longitude]
  }, [value])

  return (
    <div className="h-80 overflow-hidden rounded-xl border border-gray-200">
      <MapContainer center={center} zoom={DEFAULT_ZOOM} className="h-full w-full" scrollWheelZoom>
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickHandler onChange={onChange} />

        {markerPosition && (
          <MapMarker position={markerPosition} icon={markerIcon} onChange={onChange} />
        )}
      </MapContainer>
    </div>
  )
}

// TODO
//setCenter() не меняет центр уже созданного Leaflet map. поэтому для production-компонента нужно добавить отдельный MapController, который делает map.flyTo() при выборе результата геокодинга
