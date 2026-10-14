import { useRef } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ImagePlus } from 'lucide-react'
import { FormProvider } from 'react-hook-form'
import type Slider from 'react-slick'

import { FormInput } from '@/components/ui/form-input'
import ImagesGallery from '@/components/ui/images-gallery'

import Modal from '@/components/ui/modal'
import { useAppForm } from '@/hooks/use-app-form'
import {
  deleteExecutorVehiclePhoto,
  updateExecutorVehicle,
  uploadExecutorVehiclePhotos,
  type VehicleUpdatePayload,
} from '@/lib/executorAccount/vehicles'
import { CAR_BRAND_NAMES } from '@/consts/carBrands'

import type { Car } from '@/types/car'
import { vehicleEditSchema, VehicleEditValues } from '@/schemas/car/vehicleEditSchema'

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
export default EditVehicleModal
