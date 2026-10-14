import { useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CalendarDays, Gauge, Hash, Pencil, Ruler, Trash2, Truck } from 'lucide-react'

import type Slider from 'react-slick'

import ImagesGallery from '@/components/ui/images-gallery'
import CarDetail from './details'
import EditVehicleModal from './edit-popup'

import Modal from '@/components/ui/modal'

import { deleteExecutorVehicle } from '@/lib/executorAccount/vehicles'
import { CAR_BRAND_NAMES } from '@/consts/carBrands'
import { CarTypesNames } from '@/schemas/car/carSchema'
import type { Car } from '@/types/car'

interface CarCardProps {
  car: Car
}

const CarCard = ({ car }: CarCardProps) => {
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const queryClient = useQueryClient()
  const brandName = CAR_BRAND_NAMES[car.brand] ?? car.brand
  const carTypeName = car.car_type ? CarTypesNames[car.car_type] : null
  const sliderRef = useRef<Slider | null>(null)
  const galleryItems = car.photos ?? []
  const deleteMutation = useMutation({
    mutationFn: () => deleteExecutorVehicle(car.id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['current-executor'] })
      setIsDeleteOpen(false)
    },
  })

  return (
    <>
      <article className="overflow-hidden rounded-xl border border-gray-200 bg-white">
        <div className="flex flex-col">
          <div className="relative">
            {galleryItems.length > 0 ? (
              <div aria-label={`Фотографии: ${brandName} ${car.model}`}>
                <ImagesGallery items={galleryItems} sliderRef={sliderRef} />
              </div>
            ) : (
              <div className="flex h-48 w-full items-center justify-center bg-gray-50 text-gray-300 sm:h-56">
                <Truck className="size-12" strokeWidth={1.25} />
              </div>
            )}
          </div>

          <div className="min-w-0 p-4 sm:p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="truncate text-lg font-semibold text-gray-900">
                  {brandName} {car.model}
                </h2>
                {carTypeName && <p className="mt-0.5 text-sm text-gray-500">{carTypeName}</p>}
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-md bg-gray-100 px-2.5 py-1.5 text-sm font-semibold text-gray-800">
                  <Hash className="size-3.5 text-gray-500" />
                  {car.license_plate}
                </span>
                <button
                  type="button"
                  title="Редактировать автомобиль"
                  aria-label="Редактировать автомобиль"
                  onClick={() => setIsEditOpen(true)}
                  className="flex size-9 items-center justify-center rounded-lg border border-gray-200 text-gray-500 transition-colors hover:border-orange-300 hover:bg-orange-50 hover:text-orange-600"
                >
                  <Pencil className="size-4" />
                </button>
                <button
                  type="button"
                  title="Удалить автомобиль"
                  aria-label="Удалить автомобиль"
                  onClick={() => setIsDeleteOpen(true)}
                  className="flex size-9 items-center justify-center rounded-lg border border-gray-200 text-gray-500 transition-colors hover:border-red-200 hover:bg-red-50 hover:text-red-600"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            </div>

            <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-4">
              <CarDetail
                icon={<Gauge />}
                label="Грузоподъёмность"
                value={`${car.cargo_capacity} кг`}
              />
              {car.volume_capacity != null && (
                <CarDetail icon={<Ruler />} label="Объём" value={`${car.volume_capacity} м³`} />
              )}
              <CarDetail
                icon={<CalendarDays />}
                label="Год выпуска"
                value={String(car.manufacture_year)}
              />
              {car.price_per_km != null && (
                <CarDetail icon={<Gauge />} label="Цена за км" value={`${car.price_per_km} руб.`} />
              )}
              {car.VIN && <CarDetail icon={<Hash />} label="VIN" value={car.VIN} wide wrapValue />}
            </dl>
          </div>
        </div>
      </article>
      {isEditOpen && <EditVehicleModal car={car} onClose={() => setIsEditOpen(false)} />}
      <Modal
        isOpen={isDeleteOpen}
        onClose={() => !deleteMutation.isPending && setIsDeleteOpen(false)}
        title="Удалить автомобиль"
      >
        <div className="space-y-5 p-4 sm:p-6">
          <p className="text-sm leading-6 text-gray-600">
            Удалить {brandName} {car.model} из списка автомобилей?
          </p>
          {deleteMutation.isError && (
            <p role="alert" className="text-sm text-red-600">
              {deleteMutation.error.message || 'Не удалось удалить автомобиль'}
            </p>
          )}
          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={() => setIsDeleteOpen(false)}
              disabled={deleteMutation.isPending}
              className="h-11 rounded-lg border border-gray-200 px-4 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              Отмена
            </button>
            <button
              type="button"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
              className="h-11 rounded-lg bg-red-600 px-4 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60"
            >
              {deleteMutation.isPending ? 'Удаляем...' : 'Удалить'}
            </button>
          </div>
        </div>
      </Modal>
    </>
  )
}

export default CarCard
