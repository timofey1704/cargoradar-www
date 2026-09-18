import { CarFront, Cog, Package, Truck } from 'lucide-react'

const services = [
  {
    icon: Truck,
    title: 'Перевозчики',
    description: 'Найдите транспорт и исполнителя для перевозки вашего груза.',
  },
  {
    icon: Package,
    title: 'Поставщики запчастей',
    description: 'Находите необходимые запчасти и комплектующие для транспорта.',
  },
  {
    icon: Cog,
    title: 'СТО',
    description: 'Выбирайте сервисные станции для обслуживания и ремонта автомобилей.',
  },
  {
    icon: CarFront,
    title: 'Эвакуаторы',
    description: 'Быстро найдите эвакуатор, когда транспорт не может продолжить движение.',
  },
]

const Services = () => {
  return (
    <section className="bg-[#f7f7f5] py-20 sm:py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl">
          <span className="text-orange text-sm font-semibold">ВОЗМОЖНОСТИ</span>

          <h2 className="text-text mt-3">Всё необходимое для транспорта в одном месте</h2>

          <p className="mt-4 text-base leading-7 text-gray-500">
            CargoRadar объединяет заказчиков и разных исполнителей, связанных с грузовыми
            перевозками.
          </p>
        </div>

        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {services.map(service => {
            const Icon = service.icon

            return (
              <div
                key={service.title}
                className="group rounded-2xl bg-white p-6 transition-all hover:-translate-y-1 hover:shadow-xl"
              >
                <div className="bg-orange/10 group-hover:bg-orange flex size-14 items-center justify-center rounded-2xl transition-colors">
                  <Icon className="text-orange size-7 transition-colors group-hover:text-white" />
                </div>

                <h3 className="text-text mt-7 text-xl font-semibold">{service.title}</h3>

                <p className="mt-3 text-sm leading-6 text-gray-500">{service.description}</p>

                <div className="bg-orange mt-6 h-1 w-10 rounded-full transition-all group-hover:w-16" />
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

export default Services
