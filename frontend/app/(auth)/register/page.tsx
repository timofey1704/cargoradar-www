import Link from 'next/link'
import { ArrowRight, Truck, User } from 'lucide-react'

const LoginPage = () => {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col justify-center px-4 py-10 sm:px-6">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Регистрация в CargoRadar
          </h1>

          <p className="mt-3 text-sm text-gray-500 sm:text-base">
            Выберите тип аккаунта, чтобы продолжить
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          <Link
            href="/register/client"
            className="group rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-orange-300 hover:shadow-md sm:p-8"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-orange-50 text-orange-500">
              <User size={28} />
            </div>

            <div className="mt-6">
              <h2 className="text-xl font-semibold text-gray-900">Я клиент</h2>

              <p className="mt-2 min-h-12 text-sm leading-6 text-gray-500">
                Ищу перевозчика и хочу разместить заявку на перевозку.
              </p>
            </div>

            <div className="mt-8 flex items-center gap-2 text-sm font-medium text-orange-500">
              Войти как клиент
              <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
            </div>
          </Link>

          <Link
            href="/register/executor"
            className="group rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-orange-300 hover:shadow-md sm:p-8"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-orange-50 text-orange-500">
              <Truck size={28} />
            </div>

            <div className="mt-6">
              <h2 className="text-xl font-semibold text-gray-900">Я исполнитель</h2>

              <p className="mt-2 min-h-12 text-sm leading-6 text-gray-500">
                Хочу находить заказы и предоставлять транспортные услуги.
              </p>
            </div>

            <div className="mt-8 flex items-center gap-2 text-sm font-medium text-orange-500">
              Войти как исполнитель
              <ArrowRight size={18} className="transition-transform group-hover:translate-x-1" />
            </div>
          </Link>
        </div>

        <p className="mt-8 text-center text-xs text-gray-400">
          Если у вас уже есть аккаунт,{' '}
          <Link href="/login" className="text-orange-500 hover:underline">
            то войдите в него.
          </Link>
        </p>
      </div>
    </main>
  )
}

export default LoginPage
