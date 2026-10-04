import { SearchResults } from '@/components/search/search-results'
import { getFeed } from '@/lib/search/get-feed'

const SuppliersPage = async () => {
  const feed = await getFeed()
  const items = feed.items.filter(item => item.kind === 'post')

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <span className="text-orange text-sm font-semibold tracking-[0.12em] uppercase">
          Поставщики
        </span>
        <h1 className="text-text mt-3 text-3xl font-bold">Запчасти и комплектующие</h1>
      </div>

      <SearchResults
        items={items}
        emptyTitle="Поставщиков пока нет"
        emptyDescription="Здесь будут отображаться публикации поставщиков и производителей комплектующих."
      />
    </main>
  )
}

export default SuppliersPage
