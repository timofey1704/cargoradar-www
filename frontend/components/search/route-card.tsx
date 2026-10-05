import { ArrowRight, Clock3, MapPin } from 'lucide-react'

import { type SearchFeedItem } from '@/lib/search/get-feed'

import { formatDateTime } from '@/lib/utils/datetime-formatter'

function RouteCard({ item }: { item: Extract<SearchFeedItem, { kind: 'route' }> }) {
  const route = item.route

  if (!route) {
    return null
  }

  return (
    <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="bg-orange/10 text-orange rounded-full px-2.5 py-1 text-xs font-semibold tracking-[0.08em] uppercase">
            Маршрут
          </span>
          <span className="text-xs text-gray-400">#{item.id}</span>
        </div>

        <ArrowRight size={18} className="text-gray-300" />
      </div>

      <div className="mt-4 rounded-xl bg-gray-50 p-4">
        <div className="flex gap-3">
          <div className="flex w-4 shrink-0 flex-col items-center pt-1">
            <div className="border-orange h-2.5 w-2.5 rounded-full border-2 bg-white" />
            <div className="my-1 h-8 w-px bg-gray-300" />
            <MapPin size={14} className="text-orange" />
          </div>

          <div className="min-w-0 flex-1 space-y-2">
            <p className="text-text truncate text-sm font-semibold">{route.point_a}</p>
            <p className="text-text truncate text-sm font-semibold">{route.point_b}</p>
          </div>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-3 text-sm text-gray-500">
        {route.distance_km !== null && route.distance_km !== undefined && (
          <span>{route.distance_km.toFixed(1)} км</span>
        )}
        {route.duration_min !== null && route.duration_min !== undefined && (
          <span>{route.duration_min} мин</span>
        )}
        {route.price !== null && route.price !== undefined && (
          <span className="text-text font-semibold">{route.price.toLocaleString('ru-RU')} BYN</span>
        )}
      </div>

      {route.comment && (
        <p className="mt-4 line-clamp-2 text-sm leading-6 text-gray-600">{route.comment}</p>
      )}

      <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1.5">
          <Clock3 size={14} /> {formatDateTime(item.created_at)}
        </span>
        <span>Исполнитель #{route.executor_id}</span>
      </div>
    </article>
  )
}

export default RouteCard
