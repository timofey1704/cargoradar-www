import { SearchResults } from '@/components/search/search-results'
import { SearchResultsLayout } from '@/components/layouts/search-results-layout'
import { SearchFeedHighlight } from '@/components/search/search-feed-highlight'
import { searchCategories } from '@/config/navigation'
import { getFeed } from '@/lib/search/get-feed'

const SearchPage = async () => {
  const feed = await getFeed()
  const mapPoints = feed.items.flatMap(item =>
    item.map_points.slice(0, 1).map(point => {
      const route = item.kind === 'route' ? item.route : null
      const request = item.kind === 'request' ? item.request : null
      const itemId = `${item.kind}-${item.id}`

      return {
        ...point,
        id: `${itemId}-0`,
        itemId,
        kind: item.kind === 'route' ? 'Маршрут водителя' : 'Заявка на перевозку',
        from: route?.point_a ?? request?.origin_address ?? null,
        to: route?.point_b ?? request?.destination_address ?? null,
        price: route?.price ?? request?.budget ?? null,
        priceLabel: route ? 'Цена' : request ? 'Бюджет' : null,
        feedItem: item,
      }
    })
  )

  return (
    <main className="mx-auto max-w-[1600px] px-4 py-8 sm:px-6 lg:px-8">
      <SearchFeedHighlight />
      <section className="from-orange/10 ring-orange/10 rounded-3xl bg-linear-to-br via-white to-white p-8 shadow-sm ring-1">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <span className="text-orange text-sm font-semibold tracking-[0.12em] uppercase">
              Поиск
            </span>
            <h1 className="text-text mt-3 text-3xl font-bold sm:text-4xl">
              Перевозки рядом с вами
            </h1>
            <p className="mt-3 text-base leading-7 text-gray-600">
              Актуальные заявки и маршруты с точками отправления и назначения на карте.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {searchCategories.map(category => (
              <a
                key={category.id}
                href={category.href}
                className="hover:border-orange hover:text-orange inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 transition"
              >
                <category.icon size={16} />
                {category.title}
              </a>
            ))}
          </div>
        </div>
      </section>

      <SearchResultsLayout points={mapPoints} total={feed.total}>
        <SearchResults
          items={feed.items}
          emptyTitle="Пока нет публикаций"
          emptyDescription="Новые маршруты и заявки появятся здесь."
        />
      </SearchResultsLayout>
    </main>
  )
}

export default SearchPage
