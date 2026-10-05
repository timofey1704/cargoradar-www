import { Package } from 'lucide-react'

import {
  type SearchCategoryKey,
  type SearchFeedItem,
  getCategoryItems,
} from '@/lib/search/get-feed'

import RequestCard from './request-card'
import RouteCard from './route-card'
import PostCard from './post-card'

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
