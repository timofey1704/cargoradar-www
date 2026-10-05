'use client'

import { useState, type ReactNode } from 'react'

import { SearchMap, type SearchMapMarker } from '../search/search-map'

export function SearchResultsLayout({
  points,
  total,
  children,
}: {
  points: SearchMapMarker[]
  total: number
  children: ReactNode
}) {
  const [showMap, setShowMap] = useState(false)

  return (
    <>
      <div className="mt-8 grid gap-6 pb-20 lg:grid-cols-2 lg:items-stretch lg:pb-0">
        <section className={`min-w-0 ${showMap ? 'hidden lg:block' : ''}`}>
          <div className="mb-5 flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium tracking-[0.08em] text-gray-400 uppercase">Лента</p>
              <h2 className="text-text mt-1 text-2xl font-bold">Все результаты</h2>
            </div>
            <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">
              {total} записей
            </span>
          </div>
          {children}
        </section>

        <aside className={`${showMap ? '' : 'hidden lg:block'} min-w-0`}>
          <div className="lg:sticky lg:top-6">
            <SearchMap points={points} />
          </div>
        </aside>
      </div>

      <button
        type="button"
        aria-pressed={showMap}
        onClick={() => setShowMap(value => !value)}
        className="bg-text fixed inset-x-4 bottom-4 z-40 rounded-full px-5 py-3.5 text-sm font-semibold text-white shadow-lg lg:hidden"
      >
        {showMap ? 'Список' : 'Карта'}
      </button>
    </>
  )
}
