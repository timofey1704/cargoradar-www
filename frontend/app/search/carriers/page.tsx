import { SearchResults } from '@/components/search/search-results'
import { getFeed } from '@/lib/search/get-feed'

const CarriersPage = async () => {
  const feed = await getFeed()
  const items = feed.items.filter(item => item.kind === 'route')

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <span className="text-orange text-sm font-semibold tracking-[0.12em] uppercase">
          Перевозчики
        </span>
        <h1 className="text-text mt-3 text-3xl font-bold">Маршруты водителей</h1>
      </div>

      <SearchResults
        items={items}
        emptyTitle="Маршрутов пока нет"
        emptyDescription="На этой странице появятся актуальные маршруты водителей после загрузки данных."
      />
    </main>
  )
}

export default CarriersPage
