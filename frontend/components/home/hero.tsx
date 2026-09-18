import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, MapPin, Truck } from 'lucide-react'

const Hero = () => {
  return (
    <section className="relative overflow-hidden bg-[#f7f7f5]">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid min-h-170 items-center gap-12 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:py-20">
          <div className="relative z-10 max-w-2xl">
            <div className="border-orange/20 bg-orange/10 text-orange mb-6 inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium">
              <span className="bg-orange size-2 rounded-full" />
              Платформа для грузоперевозок
            </div>

            <h1 className="text-text max-w-xl text-4xl leading-tight font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Перевозки без лишних поисков
            </h1>

            <p className="mt-6 max-w-xl text-base leading-7 text-gray-500 sm:text-lg sm:leading-8">
              Находите подходящего перевозчика для вашего груза или получайте новые заказы в одном
              месте.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/register/client"
                className="bg-orange inline-flex h-13 items-center justify-center gap-2 rounded-xl px-6 text-sm font-semibold text-white transition-colors hover:bg-[#e95825]"
              >
                Найти перевозчика
                <ArrowRight className="size-4" />
              </Link>

              <Link
                href="/register/executor"
                className="text-text inline-flex h-13 items-center justify-center rounded-xl border border-gray-200 bg-white px-6 text-sm font-semibold transition-colors hover:border-gray-300 hover:bg-gray-50"
              >
                Стать исполнителем
              </Link>
            </div>

            <div className="mt-10 flex flex-wrap gap-x-8 gap-y-4 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-white shadow-sm">
                  <Truck className="text-orange size-4" />
                </div>
                Проверенные исполнители
              </div>

              <div className="flex items-center gap-2">
                <div className="flex size-8 items-center justify-center rounded-lg bg-white shadow-sm">
                  <MapPin className="text-orange size-4" />
                </div>
                Удобный поиск
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="bg-orange/10 absolute -right-20 -bottom-20 size-80 rounded-full blur-3xl" />

            <div className="relative overflow-hidden rounded-4xl">
              <Image
                src="/images/hero-truck.jpeg"
                alt="Грузовой автомобиль на дороге"
                width={1000}
                height={760}
                priority
                className="h-105 w-full object-cover sm:h-130 lg:h-145"
              />

              <div className="absolute inset-0 bg-linear-to-t from-black/35 via-transparent to-transparent" />

              <div className="absolute right-5 bottom-5 left-5 rounded-2xl border border-white/30 bg-white/90 p-4 backdrop-blur-md sm:right-auto sm:bottom-6 sm:left-6 sm:min-w-75">
                <div className="flex items-center gap-3">
                  <div className="bg-orange flex size-11 shrink-0 items-center justify-center rounded-xl">
                    <Truck className="size-5 text-white" />
                  </div>

                  <div>
                    <p className="text-text text-sm font-semibold">Подходящий транспорт</p>
                    <p className="mt-0.5 text-xs text-gray-500">для вашего маршрута</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="absolute -top-5 -right-5 hidden rounded-2xl bg-white p-4 shadow-xl sm:block">
              <p className="text-xs text-gray-400">CargoRadar</p>
              <p className="text-text mt-1 text-lg font-bold">Всё для перевозок</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero
