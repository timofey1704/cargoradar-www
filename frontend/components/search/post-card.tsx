import { CarFront, Clock3, Package, Wrench } from 'lucide-react'

import { type SearchFeedItem } from '@/lib/search/get-feed'

import { formatDateTime } from '@/lib/utils/datetime-formatter'

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

export default PostCard
