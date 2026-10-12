'use client'

import { useMutation } from '@tanstack/react-query'
import { FormProvider, useWatch } from 'react-hook-form'
import { z } from 'zod'

import { useAppForm } from '@/hooks/use-app-form'
import { createExecutorVehicles } from '@/lib/executorAccount/vehicles'
import { carSchema } from '@/schemas/car/carSchema'
import CarrierFields from '@/app/(auth)/register/executor/components/CarrierFields'

const createCarsSchema = z.object({
  cars: z.array(carSchema).min(1, 'Добавьте хотя бы один автомобиль'),
})

interface CreateCarProps {
  onCreated?: () => void
}

export default function CreateCar({ onCreated }: CreateCarProps) {
  const { form, handleSubmit } = useAppForm({
    schema: createCarsSchema,
    defaultValues: { cars: [] },
  })

  const cars = useWatch({ control: form.control, name: 'cars' })
  const hasCars = Array.isArray(cars) && cars.length > 0

  const createCars = useMutation({
    mutationFn: createExecutorVehicles,
    onSuccess: () => {
      form.reset({ cars: [] })
      onCreated?.()
    },
  })

  const submit = handleSubmit(async values => {
    await createCars.mutateAsync(values.cars)
  })

  return (
    <FormProvider {...form}>
      <form onSubmit={submit} className="space-y-5">
        <CarrierFields />

        {createCars.isError && (
          <p role="alert" className="text-sm font-medium text-red-600">
            {createCars.error.message || 'Не удалось добавить автомобили'}
          </p>
        )}

        {hasCars && (
          <button
            type="submit"
            disabled={createCars.isPending}
            className="flex h-12 w-full items-center justify-center rounded-xl bg-orange-500 px-5 text-sm font-semibold text-white transition-colors hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {createCars.isPending ? 'Сохраняем...' : 'Сохранить автомобили'}
          </button>
        )}
      </form>
    </FormProvider>
  )
}
