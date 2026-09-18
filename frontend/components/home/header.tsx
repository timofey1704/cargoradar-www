import Link from 'next/link'
import { ChevronDown } from 'lucide-react'
import Scroll from '@/hooks/use-scroll'
import { searchCategories } from '@/config/navigation'

const Header = () => {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="text-text shrink-0 text-xl font-bold tracking-tight">
          Cargo<span className="text-orange">Radar</span>
        </Link>

        <nav className="hidden items-center gap-8 lg:flex">
          <details className="group relative">
            <summary className="text-text hover:text-orange flex cursor-pointer list-none items-center gap-1.5 text-sm font-medium transition-colors">
              Найти исполнителя
              <ChevronDown className="size-4 transition-transform duration-200 group-open:rotate-180" />
            </summary>

            <div className="absolute top-full left-1/2 z-50 mt-4 w-145 -translate-x-1/2 rounded-2xl border border-gray-200 bg-white p-3 shadow-xl">
              <div className="grid grid-cols-2 gap-1">
                {searchCategories.map(category => {
                  const Icon = category.icon

                  return (
                    <Link
                      key={category.id}
                      href={category.href}
                      className="group/item flex gap-3 rounded-xl p-4 transition-colors hover:bg-gray-50"
                    >
                      <div className="bg-orange/10 group-hover/item:bg-orange flex size-10 shrink-0 items-center justify-center rounded-xl transition-colors">
                        <Icon className="text-orange size-5 transition-colors group-hover/item:text-white" />
                      </div>

                      <div>
                        <p className="text-text text-sm font-semibold">{category.title}</p>

                        <p className="mt-1 text-xs leading-5 text-gray-500">
                          {category.description}
                        </p>
                      </div>
                    </Link>
                  )
                })}
              </div>

              <div className="mt-2 border-t border-gray-100 px-4 py-3">
                <Link href="/search" className="text-orange text-sm font-medium hover:underline">
                  Посмотреть всех исполнителей →
                </Link>
              </div>
            </div>
          </details>

          <Scroll
            moveTo="how-it-works"
            className="text-text hover:text-orange cursor-pointer text-sm! font-medium transition-colors"
          >
            Как это работает
          </Scroll>

          <Scroll
            moveTo="faq"
            className="text-text hover:text-orange cursor-pointer text-sm! font-medium transition-colors"
          >
            FAQ
          </Scroll>
        </nav>

        <div className="hidden items-center gap-3 lg:flex">
          <Link
            href="/login"
            className="text-text rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors hover:bg-gray-50"
          >
            Войти
          </Link>

          <Link
            href="/register/client"
            className="bg-orange rounded-xl px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#e95825]"
          >
            Регистрация
          </Link>
        </div>

        <details className="group relative lg:hidden">
          <summary className="text-text flex size-10 cursor-pointer list-none items-center justify-center rounded-xl bg-gray-50">
            <span className="text-xl leading-none">☰</span>
          </summary>

          <div className="absolute top-14 right-0 z-50 w-[calc(100vw-2rem)] max-w-sm rounded-2xl border border-gray-200 bg-white p-3 shadow-xl">
            <nav className="space-y-1">
              <p className="px-3 py-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">
                Найти исполнителя
              </p>

              {searchCategories.map(category => {
                const Icon = category.icon

                return (
                  <Link
                    key={category.href}
                    href={category.href}
                    className="flex items-center gap-3 rounded-xl px-3 py-3 hover:bg-gray-50"
                  >
                    <Icon className="text-orange size-5" />
                    <span className="text-text text-sm font-medium">{category.title}</span>
                  </Link>
                )
              })}

              <div className="my-2 border-t border-gray-100" />

              <Link
                href="/how-it-works"
                className="text-text block rounded-xl px-3 py-3 text-sm font-medium hover:bg-gray-50"
              >
                Как это работает
              </Link>

              <Link
                href="/faq"
                className="text-text block rounded-xl px-3 py-3 text-sm font-medium hover:bg-gray-50"
              >
                FAQ
              </Link>

              <div className="my-2 border-t border-gray-100" />

              <Link
                href="/login"
                className="text-text block rounded-xl px-3 py-3 text-sm font-medium hover:bg-gray-50"
              >
                Войти
              </Link>

              <Link
                href="/register/client"
                className="bg-orange block rounded-xl px-3 py-3 text-center text-sm font-semibold text-white"
              >
                Регистрация
              </Link>
            </nav>
          </div>
        </details>
      </div>
    </header>
  )
}

export default Header
