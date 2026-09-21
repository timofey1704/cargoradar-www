'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ChevronDown, User } from 'lucide-react'
import Scroll from '@/hooks/use-scroll'
import { searchCategories } from '@/config/navigation'
import useClientStore from '@/store/clientStore'
import useExecutorStore from '@/store/executorStore'

const Header = () => {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setIsOpen(false)
    }

    // уводим меню в закрытое состояние при переходе на десктопный брейкпоинт
    const handleResize = () => {
      if (window.innerWidth >= 1024) setIsOpen(false)
    }

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('resize', handleResize)

    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('resize', handleResize)
    }
  }, [isOpen])

  const closeMenu = () => setIsOpen(false)

  const client = useClientStore(state => state.client)
  const executor = useExecutorStore(state => state.executor)

  // пользователь считается авторизованным, если заполнен стор клиента или исполнителя
  const user = client ?? executor
  const accountHref = client ? '/account' : '/executor'
  const userName = user?.name || 'Пользователь'

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
          {user ? (
            <Link
              href={accountHref}
              className="text-text flex items-center gap-2 rounded-xl bg-gray-100 px-4 py-2.5 text-sm font-semibold transition-colors hover:bg-gray-50"
            >
              <User className="text-orange size-4 shrink-0" />
              <span className="max-w-40 truncate">{userName}</span>
            </Link>
          ) : (
            <>
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
            </>
          )}
        </div>

        <button
          type="button"
          onClick={() => setIsOpen(prev => !prev)}
          aria-label={isOpen ? 'Закрыть меню' : 'Открыть меню'}
          aria-expanded={isOpen}
          aria-controls="mobile-menu"
          className="text-text flex size-10 items-center justify-center rounded-xl bg-gray-50 transition-colors hover:bg-gray-100 lg:hidden"
        >
          <span className="relative block h-4 w-5">
            <span
              className={`bg-text absolute left-0 h-0.5 w-5 rounded-full transition-all duration-300 ease-in-out ${
                isOpen ? 'top-1.5 rotate-45' : 'top-0'
              }`}
            />
            <span
              className={`bg-text absolute top-1.5 left-0 h-0.5 w-5 rounded-full transition-all duration-300 ease-in-out ${
                isOpen ? 'scale-x-0 opacity-0' : 'scale-x-100 opacity-100'
              }`}
            />
            <span
              className={`bg-text absolute left-0 h-0.5 w-5 rounded-full transition-all duration-300 ease-in-out ${
                isOpen ? 'top-1.5 -rotate-45' : 'top-3'
              }`}
            />
          </span>
        </button>

        <div
          id="mobile-menu"
          className={`absolute inset-x-0 top-full z-40 origin-top overflow-hidden border-b border-gray-100 bg-white shadow-xl transition-all duration-300 ease-in-out lg:hidden ${
            isOpen
              ? 'visible h-[calc(100vh-4.5rem)] scale-y-100 opacity-100'
              : 'pointer-events-none invisible h-0 scale-y-0 opacity-0'
          }`}
        >
          <nav
            className={`h-full overflow-y-auto px-4 py-4 transition-all duration-300 ease-in-out ${
              isOpen ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
            }`}
          >
            <p className="px-3 py-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">
              Найти исполнителя
            </p>

            {searchCategories.map(category => {
              const Icon = category.icon

              return (
                <Link
                  key={category.href}
                  href={category.href}
                  onClick={closeMenu}
                  className="text-text flex items-center gap-3 rounded-xl px-3 py-3 transition-colors hover:bg-gray-50"
                >
                  <Icon className="text-orange size-5" />
                  <span className="text-sm font-medium">{category.title}</span>
                </Link>
              )
            })}

            <div className="my-2 border-t border-gray-100" />

            <Scroll
              moveTo="how-it-works"
              onClick={closeMenu}
              className="text-text cursor-pointer rounded-xl px-3 py-3 text-sm font-medium transition-colors hover:bg-gray-50"
            >
              Как это работает
            </Scroll>

            <Scroll
              moveTo="faq"
              onClick={closeMenu}
              className="text-text cursor-pointer rounded-xl px-3 py-3 text-sm font-medium transition-colors hover:bg-gray-50"
            >
              FAQ
            </Scroll>

            <div className="my-2 border-t border-gray-100" />

            {user ? (
              <Link
                href={accountHref}
                onClick={closeMenu}
                className="text-text flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-colors hover:bg-gray-50"
              >
                <User className="text-orange size-5 shrink-0" />
                <span className="truncate">Здравствуйте, {userName}!</span>
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={closeMenu}
                  className="text-text block rounded-xl px-3 py-3 text-sm font-medium transition-colors hover:bg-gray-50"
                >
                  Войти
                </Link>

                <Link
                  href="/register/client"
                  onClick={closeMenu}
                  className="bg-orange block rounded-xl px-3 py-3 text-center text-sm font-semibold text-white transition-colors hover:bg-[#e95825]"
                >
                  Регистрация
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header
