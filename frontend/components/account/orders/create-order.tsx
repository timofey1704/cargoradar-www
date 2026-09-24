'use client'

import { FormProvider } from 'react-hook-form'

import { FormInput } from '@/components/ui/form-input'
import { FormSelect } from '@/components/ui/form-select'
import { RoutePointInput } from './route-point-input'
import { RouteMap } from '@/components/map/route-map'
import { Button } from '@/components/ui/button'

import { useAppForm } from '@/hooks/use-app-form'
import { useCreateClientOrder } from '@/hooks/use-client-orders'

import { createOrderSchema, type CreateOrderFormValues } from '@/schemas/account/create-order'

import type { CreateCargoRequest } from '@/types/cargo-request'

interface CreateOrderProps {
  onCreated?: () => void
}

const DEFAULT_VALUES: CreateOrderFormValues = {
  origin: {
    address: '',
    location: null,
  },

  destination: {
    address: '',
    location: null,
  },

  cargo_type: '',
  weight_kg: undefined as never,
  volume_m3: null,
  vehicle_type: null,
  loading_date: '',
  budget: null,
  comment: null,
}

const VEHICLE_OPTIONS = [
  {
    value: 'тент',
    label: 'Тент',
  },
  {
    value: 'рефрижератор',
    label: 'Рефрижератор',
  },
  {
    value: 'бортовой',
    label: 'Бортовой',
  },
  {
    value: 'фургон',
    label: 'Фургон',
  },
  {
    value: 'самосвал',
    label: 'Самосвал',
  },
  {
    value: 'другое',
    label: 'Другое',
  },
]

export default function CreateOrder({ onCreated }: CreateOrderProps) {
  const { form, handleSubmit } = useAppForm({
    schema: createOrderSchema,
    defaultValues: DEFAULT_VALUES,
  })

  const createOrder = useCreateClientOrder()

  const origin = form.watch('origin')
  const destination = form.watch('destination')

  const onSubmit = async (values: CreateOrderFormValues) => {
    if (!values.origin.location || !values.destination.location) {
      return
    }

    const payload: CreateCargoRequest = {
      origin_address: values.origin.address,
      origin_location: values.origin.location,

      destination_address: values.destination.address,
      destination_location: values.destination.location,

      cargo_type: values.cargo_type,
      weight_kg: values.weight_kg,
      volume_m3: values.volume_m3,
      vehicle_type: values.vehicle_type,
      loading_date: values.loading_date,
      budget: values.budget,
      comment: values.comment,
    }

    await createOrder.mutateAsync(payload)

    form.reset(DEFAULT_VALUES)

    onCreated?.()
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        <section className="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Маршрут</h2>

            <p className="mt-1 text-sm text-gray-500">Укажите точки отправления и назначения.</p>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-5">
              <RoutePointInput
                label="Откуда"
                value={origin}
                onChange={value =>
                  form.setValue('origin', value, {
                    shouldDirty: true,
                    shouldTouch: true,
                    shouldValidate: true,
                  })
                }
              />

              <RoutePointInput
                label="Куда"
                value={destination}
                onChange={value =>
                  form.setValue('destination', value, {
                    shouldDirty: true,
                    shouldTouch: true,
                    shouldValidate: true,
                  })
                }
              />
            </div>

            <div className="lg:sticky lg:top-6 lg:self-start">
              <RouteMap origin={origin.location} destination={destination.location} />
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Информация о грузе</h2>

            <p className="mt-1 text-sm text-gray-500">
              Укажите основные параметры груза и перевозки.
            </p>
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <FormInput<CreateOrderFormValues>
              name="cargo_type"
              label="Тип груза"
              placeholder="Например, строительные материалы"
            />

            <FormInput<CreateOrderFormValues>
              name="weight_kg"
              label="Вес, кг"
              type="number"
              min={0}
              step="0.1"
              placeholder="Например, 1500"
              registerOptions={{
                valueAsNumber: true,
              }}
            />

            <FormInput<CreateOrderFormValues>
              name="volume_m3"
              label="Объём, м³"
              type="number"
              min={0}
              step="0.1"
              placeholder="Например, 12"
              registerOptions={{
                setValueAs: value => (value === '' ? null : Number(value)),
              }}
            />

            <FormSelect<CreateOrderFormValues>
              name="vehicle_type"
              label="Тип транспорта"
              options={VEHICLE_OPTIONS}
              placeholder="Не указан"
              isClearable
            />

            <FormInput<CreateOrderFormValues>
              name="loading_date"
              label="Дата загрузки"
              type="date"
            />

            <FormInput<CreateOrderFormValues>
              name="budget"
              label="Бюджет"
              type="number"
              min={0}
              step="0.01"
              placeholder="Например, 500"
              registerOptions={{
                setValueAs: value => (value === '' ? null : Number(value)),
              }}
            />
          </div>

          <div className="mt-5">
            <FormInput<CreateOrderFormValues>
              name="comment"
              label="Комментарий"
              placeholder="Дополнительная информация для перевозчика"
              className="h-28 py-3"
            />
          </div>
        </section>

        <div className="mb-6 flex justify-end">
          <Button
            type="submit"
            variant="purple"
            size="lg"
            disabled={form.formState.isSubmitting || createOrder.isPending}
            isSubmitting={createOrder.isPending}
            loadingText="Создаем..."
          >
            Создать заказ
          </Button>
        </div>

        {createOrder.isError && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
            Не удалось создать заказ. Попробуйте ещё раз.
          </div>
        )}
      </form>
    </FormProvider>
  )
}
