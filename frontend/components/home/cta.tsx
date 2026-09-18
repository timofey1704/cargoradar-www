import Link from 'next/link'
import { ArrowRight, Truck } from 'lucide-react'

const CTA = () => {
  return (
    <section className="px-4 py-16 sm:px-6 sm:py-20 lg:px-8 lg:py-24">
      <div className="mx-auto max-w-7xl">
        <div className="bg-text relative overflow-hidden rounded-[28px] px-6 py-14 sm:px-10 lg:px-16 lg:py-16">
          <div className="bg-orange/20 absolute -right-24 -bottom-32 size-96 rounded-full blur-3xl" />
          <div className="bg-orange/10 absolute -top-32 -left-24 size-72 rounded-full blur-3xl" />

          <div className="relative z-10 flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="bg-orange mb-5 flex size-12 items-center justify-center rounded-xl">
                <Truck className="size-6 text-white" />
              </div>

              <h2 className="text-white">Готовы найти подходящего исполнителя?</h2>

              <p className="mt-4 max-w-xl text-base leading-7 text-gray-400">
                Создайте заявку и начните поиск исполнителя для вашего заказа.
              </p>
            </div>

            <Link
              href="/register/client"
              className="bg-orange inline-flex h-13 shrink-0 items-center justify-center gap-2 rounded-xl px-7 text-sm font-semibold text-white transition-colors hover:bg-[#e95825]"
            >
              Создать заявку
              <ArrowRight className="size-4" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

export default CTA
