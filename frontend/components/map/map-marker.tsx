'use client'

import { Marker } from 'react-leaflet'
import type { Icon, LatLngExpression } from 'leaflet'

interface MapMarkerProps {
  position: LatLngExpression
  icon?: Icon
  onChange: (position: { latitude: number; longitude: number }) => void
}

export function MapMarker({ position, icon, onChange }: MapMarkerProps) {
  return (
    <Marker
      position={position}
      icon={icon}
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
