'use client'

import { RefreshCw, Truck } from 'lucide-react'

import CarCard from '@/components/account/garage/car-card'
import { useCurrentExecutor } from '@/hooks/use-current-executor'

const CarsList = () => {
  const { data: executor, isLoading, isError, refetch } = useCurrentExecutor()

  if (isLoading) {
    return (
      <div className="space-y-4" aria-label="Загрузка автомобилей" aria-busy="true">
        {[0, 1].map(item => (
          <div
            key={item}
            className="h-48 animate-pulse rounded-xl border border-gray-200 bg-gray-50"
          />
        ))}
      </div>
    )
  }

  if (isError || !executor) {
    return (
      <div className="flex flex-col items-center gap-3 rounded-xl border border-gray-200 bg-white px-5 py-10 text-center">
        <p className="text-sm text-gray-600">Не удалось загрузить автомобили.</p>
        <button
          type="button"
          onClick={() => void refetch()}
          className="inline-flex items-center gap-2 text-sm font-semibold text-orange-600 hover:text-orange-700"
        >
          <RefreshCw className="size-4" />
          Повторить
        </button>
      </div>
    )
  }

  if (executor.type !== 'carrier') {
    return <p className="text-sm text-gray-500">Список транспорта доступен только перевозчикам.</p>
  }

  const cars = executor.cars ?? []

  if (cars.length === 0) {
    return (
      <div className="flex flex-col items-center rounded-xl border border-dashed border-gray-300 bg-white px-5 py-12 text-center">
        <span className="mb-3 flex size-12 items-center justify-center rounded-full bg-orange-50 text-orange-600">
          <Truck className="size-6" />
        </span>
        <h2 className="text-base font-semibold text-gray-900">Автомобилей пока нет</h2>
        <p className="mt-1 text-sm text-gray-500">
          Добавьте транспорт, чтобы он появился в гараже.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500">
        {cars.length} {getCarCountLabel(cars.length)}
      </p>
      <div className="grid gap-4 xl:grid-cols-2">
        {cars.map(car => (
          <CarCard key={car.id} car={car} />
        ))}
      </div>
    </div>
  )
}

function getCarCountLabel(count: number) {
  const remainder100 = count % 100
  const remainder10 = count % 10

  if (remainder100 >= 11 && remainder100 <= 14) return 'автомобилей'
  if (remainder10 === 1) return 'автомобиль'
  if (remainder10 >= 2 && remainder10 <= 4) return 'автомобиля'
  return 'автомобилей'
}

export default CarsList
