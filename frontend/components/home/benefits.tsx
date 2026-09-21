import { Clock3, MessageSquare, ShieldCheck, SlidersHorizontal } from 'lucide-react'

const benefits = [
  {
    icon: ShieldCheck,
    title: 'Понятный выбор',
    description: 'Изучайте информацию об исполнителях и выбирайте подходящий вариант для заказа.',
  },
  {
    icon: Clock3,
    title: 'Экономия времени',
    description: 'Не нужно искать перевозчиков и сервисы по разным площадкам.',
  },
  {
    icon: MessageSquare,
    title: 'Всё по заказу в одном месте',
    description: 'Общайтесь с исполнителем и отслеживайте основные этапы выполнения заказа.',
  },
  {
    icon: SlidersHorizontal,
    title: 'Подходящий транспорт',
    description: 'Указывайте параметры груза и находите исполнителей с подходящим транспортом.',
  },
]

const Benefits = () => {
  return (
    <section className="py-20 sm:py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-14 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <span className="text-orange text-sm font-semibold">ПОЧЕМУ CARGORADAR</span>

            <h2 className="text-text mt-3 max-w-lg dark:text-white">
              Сделайте работу с перевозками проще
            </h2>

            <p className="mt-5 max-w-lg text-base leading-7 text-gray-500">
              Один сервис для поиска исполнителей, создания заказов и взаимодействия на всех этапах
              перевозки.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {benefits.map(benefit => {
              const Icon = benefit.icon

              return (
                <div
                  key={benefit.title}
                  className="rounded-2xl border border-gray-200 bg-white p-6"
                >
                  <div className="flex size-11 items-center justify-center rounded-xl bg-gray-100">
                    <Icon className="text-text size-5" />
                  </div>

                  <h3 className="text-text mt-5 text-lg font-semibold">{benefit.title}</h3>

                  <p className="mt-2 text-sm leading-6 text-gray-500">{benefit.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}

export default Benefits
