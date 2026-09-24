'use client'

import { Marker } from 'react-leaflet'
import type { LatLngExpression } from 'leaflet'

interface MapMarkerProps {
  position: LatLngExpression
  onChange: (position: { latitude: number; longitude: number }) => void
}

export function MapMarker({ position, onChange }: MapMarkerProps) {
  return (
    <Marker
      position={position}
      draggable
      eventHandlers={{
        dragend: event => {
          const marker = event.target
          const { lat, lng } = marker.getLatLng()

          onChange({
            latitude: lat,
            longitude: lng,
          })
        },
      }}
    />
  )
}
