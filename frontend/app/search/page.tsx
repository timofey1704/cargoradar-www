import { SearchResults } from '@/components/search/search-results'
import { searchCategories } from '@/config/navigation'
import { getFeed } from '@/lib/search/get-feed'

const SearchPage = async () => {
  const feed = await getFeed()

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <section className="from-orange/10 ring-orange/10 rounded-3xl bg-gradient-to-br via-white to-white p-8 shadow-sm ring-1">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <span className="text-orange text-sm font-semibold tracking-[0.12em] uppercase">
              Поиск
            </span>
            <h1 className="text-text mt-3 text-3xl font-bold sm:text-4xl">
              Найдите перевозчика, сервис или запчасти
            </h1>
            <p className="mt-3 text-base leading-7 text-gray-600">
              Лента объединяет маршруты водителей и публикации исполнителей: маршруты, сервисы,
              эвакуаторы и поставки частично.
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

      <section className="mt-10">
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
          emptyDescription="Скоро здесь появятся маршруты водителей и посты исполнителей."
        />
      </section>
    </main>
  )
}

export default SearchPage
