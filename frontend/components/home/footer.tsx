import Link from 'next/link'
import { searchCategories, legalNavigation } from '@/config/navigation'
import Scroll from '@/hooks/use-scroll'

const Footer = () => {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8 lg:py-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div className="max-w-sm">
            <Link href="/" className="text-text text-xl font-bold tracking-tight">
              Cargo<span className="text-orange">Radar</span>
            </Link>

            <p className="mt-4 text-sm leading-6 text-gray-500">
              Платформа для поиска исполнителей и организации грузоперевозок.
            </p>
          </div>

          <div>
            <h3 className="text-text text-sm font-semibold">Поиск</h3>

            <ul className="mt-5 space-y-3">
              {searchCategories.map(category => (
                <li key={category.href}>
                  <Link
                    href={category.href}
                    className="hover:text-orange text-sm text-gray-500 transition-colors"
                  >
                    {category.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-text text-sm font-semibold">CargoRadar</h3>

            <ul className="mt-5 space-y-3">
              <li>
                <Scroll
                  moveTo="how-it-works"
                  className="internal-link hover:text-orange cursor-pointer text-sm! text-gray-500"
                >
                  Как это работает
                </Scroll>
              </li>

              <li>
                <Scroll
                  moveTo="faq"
                  className="internal-link hover:text-orange cursor-pointer text-sm! text-gray-500"
                >
                  FAQ
                </Scroll>
              </li>

              <li>
                <Link href="/login" className="hover:text-orange text-sm text-gray-500">
                  Войти
                </Link>
              </li>

              <li>
                <Link href="/register/client" className="hover:text-orange text-sm text-gray-500">
                  Регистрация
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-text text-sm font-semibold">Документы</h3>

            <ul className="mt-5 space-y-3">
              {legalNavigation.map(item => (
                <li key={item.id}>
                  <Link href={item.href} className="hover:text-orange text-sm text-gray-500">
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-gray-100 pt-6 text-sm text-gray-400 sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {new Date().getFullYear()} CargoRadar. Проект создан и разработан{' '}
            <a
              href="https://t.me/mnk_mac1ntosh"
              className="hover:underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              mnk_mac1ntosh
            </a>
          </p>

          <p>Все права защищены</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
