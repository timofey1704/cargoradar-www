import { ArrowRight, Clock3, MapPin } from 'lucide-react'

import { type SearchFeedItem } from '@/lib/search/get-feed'

import { formatDateTime } from '@/lib/utils/datetime-formatter'
import { Button } from '@/components/ui/button'

function RequestCard({ item }: { item: Extract<SearchFeedItem, { kind: 'request' }> }) {
  const request = item.request

  if (!request) {
    return null
  }

  return (
    <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-center justify-between gap-4">
        <span className="bg-orange/10 text-orange rounded-full px-2.5 py-1 text-xs font-semibold">
          Заявка на перевозку
        </span>
        <span className="text-xs text-gray-400">#{item.id}</span>
      </div>

      <div className="mt-4 space-y-2">
        <p className="text-text flex items-start gap-2 text-sm font-semibold">
          <MapPin size={16} className="text-orange mt-0.5 shrink-0" />
          <span>{request.origin_address}</span>
        </p>
        <p className="text-text flex items-start gap-2 text-sm font-semibold">
          <ArrowRight size={16} className="mt-0.5 shrink-0 text-gray-400" />
          <span>{request.destination_address}</span>
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-3 text-sm text-gray-500">
        <span>{request.cargo_type}</span>
        <span>{request.weight_kg.toLocaleString('ru-RU')} кг</span>
        {request.vehicle_type && <span>{request.vehicle_type}</span>}
        {request.budget !== null && (
          <span className="text-text font-semibold">
            {request.budget.toLocaleString('ru-RU')} BYN
          </span>
        )}
      </div>

      {request.comment && (
        <p className="mt-4 line-clamp-2 text-sm leading-6 text-gray-600">{request.comment}</p>
      )}

      <div className="my-5 flex items-center justify-between border-t border-gray-100 pt-4 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1.5">
          <Clock3 size={14} /> {formatDateTime(item.created_at)}
        </span>
        <span>
          Погрузка: {new Intl.DateTimeFormat('ru-RU').format(new Date(request.loading_date))}
        </span>
      </div>
      <Button type="button" variant="blue" size="md">
        Откликнуться
      </Button>
    </article>
  )
}

export default RequestCard
