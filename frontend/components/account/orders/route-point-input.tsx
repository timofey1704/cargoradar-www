'use client'

import { useEffect, useRef, useState } from 'react'

import { Loader2, MapPin, Search } from 'lucide-react'

import { searchGeo, reverseGeo } from '@/lib/api/client/geo'
import { LocationPicker } from '@/components/map/location-picker'

import type { GeoSearchResult, RoutePointValue } from '@/types/geo'

interface RoutePointInputProps {
  label: string
  value: RoutePointValue
  onChange: (value: RoutePointValue) => void
}

export function RoutePointInput({ label, value, onChange }: RoutePointInputProps) {
  const [results, setResults] = useState<GeoSearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSearching, setIsSearching] = useState(false)

  const searchTimeout = useRef<ReturnType<typeof setTimeout> | null>(null)
  const searchController = useRef<AbortController | null>(null)

  useEffect(
    () => () => {
      if (searchTimeout.current) clearTimeout(searchTimeout.current)
      searchController.current?.abort()
    },
    []
  )

  const handleSearch = (nextQuery: string) => {
    onChange({
      address: nextQuery,
      location: null,
    })

    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current)
    }
    searchController.current?.abort()
    searchController.current = null
    setIsSearching(false)

    if (nextQuery.trim().length < 2) {
      setResults([])
      return
    }

    searchTimeout.current = setTimeout(async () => {
      const controller = new AbortController()
      searchController.current = controller
      try {
        setIsSearching(true)

        const data = await searchGeo({
          query: nextQuery.trim(),
          signal: controller.signal,
        })

        if (!controller.signal.aborted) setResults(data)
      } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) setResults([])
      } finally {
        if (searchController.current === controller) setIsSearching(false)
      }
    }, 400)
  }

  const selectResult = (result: GeoSearchResult) => {
    const nextValue: RoutePointValue = {
      address: result.displayName,
      location: {
        latitude: result.latitude,
        longitude: result.longitude,
      },
    }

    setResults([])
    onChange(nextValue)
  }

  const handleMapChange = async ({
    latitude,
    longitude,
  }: {
    latitude: number
    longitude: number
  }) => {
    onChange({
      address: '',
      location: {
        latitude,
        longitude,
      },
    })

    try {
      setIsLoading(true)

      const result = await reverseGeo({
        latitude,
        longitude,
      })

      onChange({
        address: result.address,
        location: {
          latitude: result.latitude,
          longitude: result.longitude,
        },
      })
    } catch {
      return
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium text-gray-800">{label}</label>

        <div className="relative">
          <MapPin
            size={18}
            className="absolute top-1/2 left-4 z-10 -translate-y-1/2 text-gray-400"
          />

          <input
            value={value.address}
            onChange={event => handleSearch(event.target.value)}
            placeholder="Введите адрес"
            className={[
              'h-13 w-full rounded-xl border bg-white',
              'pr-12 pl-11 text-sm text-gray-900',
              'transition-all duration-200 outline-none',
              'placeholder:text-gray-400',
              'border-gray-200',
              'focus:border-orange-500',
              'focus:ring-2 focus:ring-orange-500/15',
            ].join(' ')}
          />

          {isSearching ? (
            <Loader2
              size={18}
              className="absolute top-1/2 right-4 -translate-y-1/2 animate-spin text-orange-500"
            />
          ) : (
            <Search size={18} className="absolute top-1/2 right-4 -translate-y-1/2 text-gray-400" />
          )}

          {results.length > 0 && (
            <div className="absolute top-full right-0 left-0 z-30 mt-1 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">
              {results.map(result => (
                <button
                  key={result.placeId}
                  type="button"
                  onClick={() => selectResult(result)}
                  className="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-orange-50"
                >
                  <MapPin size={18} className="mt-0.5 shrink-0 text-orange-500" />

                  <span className="text-sm text-gray-900">{result.displayName}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="relative z-0">
        <LocationPicker value={value.location} onChange={handleMapChange} />

        {isLoading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-white/60 backdrop-blur-sm">
            <div className="flex items-center gap-2 rounded-lg bg-white px-4 py-3 text-sm text-gray-700 shadow-lg">
              <Loader2 size={16} className="animate-spin text-orange-500" />
              Определяем адрес...
            </div>
          </div>
        )}
      </div>

      {value.location && (
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <MapPin size={14} className="text-orange-500" />

          <span>
            {value.location.latitude.toFixed(6)}, {value.location.longitude.toFixed(6)}
          </span>
        </div>
      )}
    </div>
  )
}
