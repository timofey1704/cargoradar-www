'use client'

import { useMutation } from '@tanstack/react-query'
import { useQueryClient } from '@tanstack/react-query'
import { FormProvider, useWatch } from 'react-hook-form'
import { z } from 'zod'

import { useAppForm } from '@/hooks/use-app-form'
import { createExecutorVehicles } from '@/lib/executorAccount/vehicles'
import { carSchema } from '@/schemas/car/carSchema'
import CarrierFields from '@/app/(auth)/register/executor/components/CarrierFields'

import { Button } from '@/components/ui/button'

const createCarsSchema = z.object({
  cars: z.array(carSchema).min(1, 'Добавьте хотя бы один автомобиль'),
})

interface CreateCarProps {
  onCreated?: () => void
}

export default function CreateCar({ onCreated }: CreateCarProps) {
  const queryClient = useQueryClient()
  const { form, handleSubmit } = useAppForm({
    schema: createCarsSchema,
    defaultValues: { cars: [] },
  })

  const cars = useWatch({ control: form.control, name: 'cars' })
  const hasCars = Array.isArray(cars) && cars.length > 0

  const createCars = useMutation({
    mutationFn: createExecutorVehicles,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['current-executor'] })
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
          <Button
            disabled={form.formState.isSubmitting || createCars.isPending}
            variant="blue"
            isSubmitting={createCars.isPending}
            defaultText="Добавить авто"
            loadingText="Добавляем..."
            showArrow={false}
          />
        )}
      </form>
    </FormProvider>
  )
}
