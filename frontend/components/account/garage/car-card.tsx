'use client'

import { useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { CalendarDays, Gauge, Hash, ImagePlus, Pencil, Ruler, Trash2, Truck } from 'lucide-react'
import { FormProvider } from 'react-hook-form'
import type Slider from 'react-slick'
import { z } from 'zod'

import { FormInput } from '@/components/ui/form-input'
import ImagesGallery from '@/components/ui/images-gallery'
import Modal from '@/components/ui/modal'
import { useAppForm } from '@/hooks/use-app-form'
import {
  deleteExecutorVehicle,
  deleteExecutorVehiclePhoto,
  updateExecutorVehicle,
  uploadExecutorVehiclePhotos,
  type VehicleUpdatePayload,
} from '@/lib/executorAccount/vehicles'
import { CAR_BRAND_NAMES } from '@/consts/carBrands'
import { CarTypesNames } from '@/schemas/car/carSchema'
import type { Car } from '@/types/car'

const vehicleEditSchema = z.object({
  cargo_capacity: z.number().int().gt(0, 'Укажите грузоподъёмность больше 0'),
  volume_capacity: z.number().int().gt(0, 'Объём должен быть больше 0').nullable(),
  license_plate: z
    .string()
    .min(1, 'Введите номерной знак')
    .max(10, 'Номерной знак должен содержать максимум 10 символов'),
})

type VehicleEditValues = z.infer<typeof vehicleEditSchema>

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
              {car.price_per_km != null && car.price_per_km !== '' && (
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

interface EditVehicleModalProps {
  car: Car
  onClose: () => void
}

function EditVehicleModal({ car, onClose }: EditVehicleModalProps) {
  const queryClient = useQueryClient()
  const photoInputRef = useRef<HTMLInputElement>(null)
  const sliderRef = useRef<Slider | null>(null)
  const { form, handleSubmit } = useAppForm({
    schema: vehicleEditSchema,
    defaultValues: {
      cargo_capacity: car.cargo_capacity,
      volume_capacity: car.volume_capacity,
      license_plate: car.license_plate,
    },
  })

  const updateMutation = useMutation({
    mutationFn: (values: VehicleUpdatePayload) => updateExecutorVehicle(car.id, values),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['current-executor'] })
      onClose()
    },
  })
  const uploadPhotosMutation = useMutation({
    mutationFn: (photos: File[]) => uploadExecutorVehiclePhotos(car.id, photos),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['current-executor'] })
    },
  })
  const deletePhotoMutation = useMutation({
    mutationFn: (photoId: number) => deleteExecutorVehiclePhoto(car.id, photoId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['current-executor'] })
    },
  })

  const submit = handleSubmit(async values => {
    await updateMutation.mutateAsync(values)
  })

  return (
    <Modal
      isOpen
      onClose={() =>
        !updateMutation.isPending &&
        !uploadPhotosMutation.isPending &&
        !deletePhotoMutation.isPending &&
        onClose()
      }
      title={`Изменить ${CAR_BRAND_NAMES[car.brand] ?? car.brand} ${car.model}`}
    >
      <FormProvider {...form}>
        <form onSubmit={submit} className="space-y-5 p-4 sm:p-6">
          <section className="space-y-3" aria-label="Фотографии автомобиля">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold text-gray-900">
                Фотографии <span className="font-normal text-gray-500">({car.photos.length})</span>
              </h3>
              <button
                type="button"
                onClick={() => photoInputRef.current?.click()}
                disabled={uploadPhotosMutation.isPending}
                className="inline-flex h-9 shrink-0 items-center gap-2 rounded-lg border border-gray-200 px-3 text-sm font-medium text-gray-700 hover:border-orange-300 hover:bg-orange-50 hover:text-orange-600 disabled:opacity-50"
              >
                <ImagePlus className="size-4" />
                Добавить фото
              </button>
              <input
                ref={photoInputRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={event => {
                  const photos = Array.from(event.currentTarget.files ?? [])
                  event.currentTarget.value = ''
                  if (photos.length > 0) uploadPhotosMutation.mutate(photos)
                }}
              />
            </div>
            {car.photos.length > 0 ? (
              <ImagesGallery
                items={car.photos}
                sliderRef={sliderRef}
                onRemove={photoId => deletePhotoMutation.mutate(photoId)}
                removingImageId={
                  deletePhotoMutation.isPending ? deletePhotoMutation.variables : undefined
                }
              />
            ) : (
              <p className="rounded-lg border border-dashed border-gray-300 px-4 py-6 text-center text-sm text-gray-500">
                Фотографий пока нет
              </p>
            )}
            {uploadPhotosMutation.isError && (
              <p role="alert" className="text-sm text-red-600">
                {uploadPhotosMutation.error.message || 'Не удалось загрузить фотографии'}
              </p>
            )}
            {deletePhotoMutation.isError && (
              <p role="alert" className="text-sm text-red-600">
                {deletePhotoMutation.error.message || 'Не удалось удалить фотографию'}
              </p>
            )}
          </section>
          <FormInput<VehicleEditValues>
            name="cargo_capacity"
            label="Грузоподъёмность, кг"
            type="number"
            inputMode="numeric"
            min={1}
            registerOptions={{ valueAsNumber: true }}
          />
          <FormInput<VehicleEditValues>
            name="volume_capacity"
            label="Объём, м³"
            type="number"
            inputMode="numeric"
            min={1}
            registerOptions={{ setValueAs: value => (value === '' ? null : Number(value)) }}
          />
          <FormInput<VehicleEditValues>
            name="license_plate"
            label="Номерной знак"
            autoComplete="off"
          />

          {updateMutation.isError && (
            <p role="alert" className="text-sm text-red-600">
              {updateMutation.error.message || 'Не удалось сохранить изменения'}
            </p>
          )}

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={updateMutation.isPending}
              className="h-11 rounded-lg border border-gray-200 px-4 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-60"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="h-11 rounded-lg bg-orange-500 px-4 text-sm font-semibold text-white hover:bg-orange-600 disabled:opacity-60"
            >
              {updateMutation.isPending ? 'Сохраняем...' : 'Сохранить'}
            </button>
          </div>
        </form>
      </FormProvider>
    </Modal>
  )
}

interface CarDetailProps {
  icon: React.ReactNode
  label: string
  value: string
  wide?: boolean
  wrapValue?: boolean
}

function CarDetail({ icon, label, value, wide = false, wrapValue = false }: CarDetailProps) {
  return (
    <div className={wide ? 'col-span-2 min-w-0' : 'min-w-0'}>
      <dt className="flex items-center gap-1.5 text-xs text-gray-500">
        <span className="text-gray-400 [&>svg]:size-3.5">{icon}</span>
        {label}
      </dt>
      <dd
        className={`mt-1 text-sm font-medium text-gray-800 ${wrapValue ? 'break-all' : 'truncate'}`}
      >
        {value}
      </dd>
    </div>
  )
}

export default CarCard
