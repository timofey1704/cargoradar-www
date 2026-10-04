import { ArrowRight, CarFront, Clock3, MapPin, Package, Wrench } from 'lucide-react'

import {
  type SearchCategoryKey,
  type SearchFeedItem,
  getCategoryItems,
} from '@/lib/search/get-feed'

function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Без даты'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Без даты'
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

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

function PostCard({ item }: { item: Extract<SearchFeedItem, { kind: 'post' }> }) {
  const post = item.post

  if (!post) {
    return null
  }

  const isExecutor = post.creator_type === 'executor'
  const Icon = isExecutor ? CarFront : Wrench

  return (
    <article className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex size-9 items-center justify-center rounded-xl bg-gray-100 text-gray-500">
            <Icon size={18} />
          </div>
          <span className="rounded-full bg-gray-100 px-2.5 py-1 text-[10px] font-semibold tracking-[0.08em] text-gray-600 uppercase">
            {isExecutor ? 'Исполнитель' : 'Клиент'}
          </span>
        </div>
        <span className="text-xs text-gray-400">#{item.id}</span>
      </div>

      <h3 className="text-text mt-4 text-lg font-semibold">{post.title}</h3>
      <p className="mt-3 line-clamp-4 text-sm leading-6 text-gray-600">{post.request_text}</p>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-gray-500">
        {post.creator_type && (
          <span className="rounded-full bg-gray-100 px-2 py-1">{post.creator_type}</span>
        )}
        {post.client_id !== null && post.client_id !== undefined && (
          <span className="rounded-full bg-gray-100 px-2 py-1">Клиент #{post.client_id}</span>
        )}
        {post.executor_id !== null && post.executor_id !== undefined && (
          <span className="rounded-full bg-gray-100 px-2 py-1">
            Исполнитель #{post.executor_id}
          </span>
        )}
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1.5">
          <Clock3 size={14} /> {formatDateTime(item.created_at)}
        </span>
        <span className="text-orange inline-flex items-center gap-1.5">
          <Package size={14} /> Публикация
        </span>
      </div>
    </article>
  )
}

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

      <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1.5">
          <Clock3 size={14} /> {formatDateTime(item.created_at)}
        </span>
        <span>
          Погрузка: {new Intl.DateTimeFormat('ru-RU').format(new Date(request.loading_date))}
        </span>
      </div>
    </article>
  )
}

export function SearchResults({
  items,
  emptyTitle,
  emptyDescription,
}: {
  items: SearchFeedItem[]
  emptyTitle: string
  emptyDescription: string
}) {
  if (!items.length) {
    return (
      <div className="rounded-3xl border border-dashed border-gray-200 bg-gray-50 p-10 text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-white shadow-sm">
          <Package className="text-gray-400" size={20} />
        </div>
        <h3 className="text-text mt-5 text-xl font-semibold">{emptyTitle}</h3>
        <p className="mt-2 text-sm text-gray-500">{emptyDescription}</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {items.map(item =>
        item.kind === 'route' ? (
          <RouteCard key={`${item.kind}-${item.id}`} item={item} />
        ) : item.kind === 'post' ? (
          <PostCard key={`${item.kind}-${item.id}`} item={item} />
        ) : (
          <RequestCard key={`${item.kind}-${item.id}`} item={item} />
        )
      )}
    </div>
  )
}

export function SearchCategoryResults({
  category,
  items,
  emptyTitle,
  emptyDescription,
}: {
  category: SearchCategoryKey
  items: SearchFeedItem[]
  emptyTitle: string
  emptyDescription: string
}) {
  const filteredItems = getCategoryItems(items, category)

  return (
    <SearchResults
      items={filteredItems}
      emptyTitle={emptyTitle}
      emptyDescription={emptyDescription}
    />
  )
}
