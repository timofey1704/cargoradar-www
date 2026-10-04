import { SearchResults } from '@/components/search/search-results'
import { getFeed } from '@/lib/search/get-feed'

const TowTrucksPage = async () => {
  const feed = await getFeed()
  const items = feed.items.filter(item => item.kind === 'post')

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8">
        <span className="text-orange text-sm font-semibold tracking-[0.12em] uppercase">
          Эвакуаторы
        </span>
        <h1 className="text-text mt-3 text-3xl font-bold">Службы эвакуации</h1>
      </div>

      <SearchResults
        items={items}
        emptyTitle="Эвакуаторы пока не найдены"
        emptyDescription="Здесь будут попадать публикации эвакуаторных служб и операторов."
      />
    </main>
  )
}

export default TowTrucksPage
