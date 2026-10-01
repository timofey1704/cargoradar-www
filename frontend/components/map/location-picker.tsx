'use client'

import { useEffect, useMemo } from 'react'
import { MapContainer, TileLayer, useMap, useMapEvents } from 'react-leaflet'
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

interface MapControllerProps {
  value: Coordinates | null
}

function MapController({ value }: MapControllerProps) {
  const map = useMap()

  useEffect(() => {
    if (!value) {
      return
    }

    map.flyTo([value.latitude, value.longitude], map.getZoom())
  }, [map, value])

  return null
}

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
  const markerPosition = useMemo<LatLngExpression | null>(() => {
    if (!value) {
      return null
    }

    return [value.latitude, value.longitude]
  }, [value])

  return (
    <div className="h-80 overflow-hidden rounded-xl border border-gray-200">
      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        className="h-full w-full"
        scrollWheelZoom
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapController value={value} />
        <MapClickHandler onChange={onChange} />

        {markerPosition && (
          <MapMarker position={markerPosition} icon={markerIcon} onChange={onChange} />
        )}
      </MapContainer>
    </div>
  )
}
