import { SearchResults } from '@/components/search/search-results'
import { SearchMap } from '@/components/search/search-map'
import { searchCategories } from '@/config/navigation'
import { getFeed } from '@/lib/search/get-feed'

const SearchPage = async () => {
  const feed = await getFeed()
  const mapPoints = feed.items.flatMap(item =>
    item.map_points.map((point, index) => {
      const route = item.kind === 'route' ? item.route : null
      const request = item.kind === 'request' ? item.request : null

      return {
        ...point,
        id: `${item.kind}-${item.id}-${index}`,
        kind: item.kind === 'route' ? 'Маршрут водителя' : 'Заявка на перевозку',
        from: route?.point_a ?? request?.origin_address ?? null,
        to: route?.point_b ?? request?.destination_address ?? null,
        price: route?.price ?? request?.budget ?? null,
        priceLabel: route ? 'Цена' : request ? 'Бюджет' : null,
      }
    })
  )

  return (
    <main className="mx-auto max-w-[1600px] px-4 py-8 sm:px-6 lg:px-8">
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

      <div className="mt-8 grid gap-6 lg:grid-cols-2 lg:items-start">
        <section className="min-w-0">
          <div className="mb-5 flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-medium tracking-[0.08em] text-gray-400 uppercase">Лента</p>
              <h2 className="text-text mt-1 text-2xl font-bold">Все результаты</h2>
            </div>
            <span className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600">
              {feed.total} записей
            </span>
          </div>

          <SearchResults
            items={feed.items}
            emptyTitle="Пока нет публикаций"
            emptyDescription="Новые маршруты и заявки появятся здесь."
          />
        </section>

        <aside className="lg:sticky lg:top-6">
          <SearchMap points={mapPoints} />
        </aside>
      </div>
    </main>
  )
}

export default SearchPage
