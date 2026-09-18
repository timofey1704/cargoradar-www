import { CheckCircle2, FileText, Search, Star } from 'lucide-react'

const steps = [
  {
    number: '01',
    icon: FileText,
    title: 'Создайте заявку',
    description: 'Укажите маршрут, параметры груза и требования к перевозке.',
  },
  {
    number: '02',
    icon: Search,
    title: 'Получите предложения',
    description: 'Исполнители смогут увидеть вашу заявку и предложить свои услуги.',
  },
  {
    number: '03',
    icon: CheckCircle2,
    title: 'Выберите исполнителя',
    description: 'Сравните подходящие варианты и выберите исполнителя для заказа.',
  },
  {
    number: '04',
    icon: Star,
    title: 'Оцените результат',
    description: 'После выполнения заказа оставьте отзыв и оцените работу исполнителя.',
  },
]

interface HowItWorksProps {
  id: string
}

const HowItWorks: React.FC<HowItWorksProps> = ({ id }) => {
  return (
    <section className="py-20 sm:py-24 lg:py-32" id={id}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-orange text-sm font-semibold">КАК ЭТО РАБОТАЕТ</span>

          <h2 className="text-text mt-3">Перевозка в несколько простых шагов</h2>

          <p className="mt-4 text-base leading-7 text-gray-500">
            CargoRadar помогает пройти путь от создания заявки до завершения заказа в одном сервисе.
          </p>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map(step => {
            const Icon = step.icon

            return (
              <div
                key={step.number}
                className="relative rounded-2xl border border-gray-200 bg-white p-6 transition-shadow hover:shadow-lg"
              >
                <div className="flex items-start justify-between">
                  <div className="bg-orange/10 flex size-12 items-center justify-center rounded-xl">
                    <Icon className="text-orange size-6" />
                  </div>

                  <span className="text-3xl font-bold text-gray-300">{step.number}</span>
                </div>

                <h3 className="text-text mt-6 text-xl font-semibold">{step.title}</h3>

                <p className="mt-3 text-sm leading-6 text-gray-500">{step.description}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export default HowItWorks
