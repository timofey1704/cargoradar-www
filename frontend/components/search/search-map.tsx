'use client'

import dynamic from 'next/dynamic'

import type { SearchMapPoint } from '@/lib/search/get-feed'

export interface SearchMapMarker extends SearchMapPoint {
  id: string
  kind: string
}

const SearchMapCanvas = dynamic(
  () => import('./search-map-canvas').then(module => module.SearchMapCanvas),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full min-h-96 items-center justify-center rounded-xl border border-gray-200 bg-gray-100 text-sm text-gray-500">
        Загружаем карту...
      </div>
    ),
  }
)

export function SearchMap({ points }: { points: SearchMapMarker[] }) {
  return <SearchMapCanvas points={points} />
}
