import { Plus, X } from 'lucide-react'
import { useFieldArray, useFormContext } from 'react-hook-form'

import { FormInput } from '@/components/ui/form-input'
import { FormMediaInput } from '@/components/ui/form-media-input'
import { FormSelect } from '@/components/ui/form-select'
import { objectToSelectOptions } from '@/lib/utils/select'
import type { RegisterFormInput } from '@/schemas/auth/register/executorSchema'
import { CarTypesNames } from '@/schemas/car/carSchema'

import { carBrandOptions } from '../utils/carBrandOptions'
import { createEmptyCar } from '../utils/createEmptyCar'

const CarrierFields = () => {
  const form = useFormContext<RegisterFormInput>()

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'cars',
  })

  const carsError = 'cars' in form.formState.errors ? form.formState.errors.cars : undefined

  const handleAddCar = () => {
    append(createEmptyCar())
  }

  const handleRemoveCar = (index: number) => {
    remove(index)
  }

  return (
    <div className="mt-2 border-t border-gray-100 pt-6">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Транспорт</h3>
          <p className="mt-1 text-xs text-gray-500">Добавьте один или несколько автомобилей</p>
        </div>

        {fields.length > 0 && (
          <span className="text-xs font-medium text-gray-400">
            {fields.length}{' '}
            {fields.length === 1 ? 'автомобиль' : fields.length < 5 ? 'автомобиля' : 'автомобилей'}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-4">
        {fields.map((field, index) => (
          <div key={field.id} className="rounded-2xl border border-gray-200 bg-gray-50/50 p-5">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">Автомобиль {index + 1}</h3>
                <p className="mt-1 text-xs text-gray-500">Укажите характеристики автомобиля</p>
              </div>

              <button
                type="button"
                onClick={() => handleRemoveCar(index)}
                className="inline-flex items-center gap-1 text-xs font-medium text-gray-400 transition-colors hover:text-red-500"
              >
                <X className="size-3.5" />
                Удалить
              </button>
            </div>

            <div className="flex flex-col gap-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <FormSelect<RegisterFormInput>
                  name={`cars.${index}.brand`}
                  label="Марка"
                  placeholder="Выберите марку"
                  options={carBrandOptions}
                />

                <FormInput<RegisterFormInput>
                  name={`cars.${index}.model`}
                  label="Модель"
                  placeholder="TGX"
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <FormInput<RegisterFormInput>
                  name={`cars.${index}.cargo_capacity`}
                  label="Грузоподъёмность, т"
                  placeholder="20"
                  type="number"
                  inputMode="numeric"
                  min={1}
                  registerOptions={{
                    valueAsNumber: true,
                  }}
                />

                <FormInput<RegisterFormInput>
                  name={`cars.${index}.volume_capacity`}
                  label="Объём, м³"
                  placeholder="82"
                  type="number"
                  inputMode="numeric"
                  min={1}
                  registerOptions={{
                    valueAsNumber: true,
                  }}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <FormSelect<RegisterFormInput>
                  name={`cars.${index}.car_type`}
                  label="Тип кузова"
                  placeholder="Выберите тип кузова"
                  options={objectToSelectOptions(CarTypesNames)}
                />

                <FormInput<RegisterFormInput>
                  name={`cars.${index}.manufacture_year`}
                  label="Год выпуска"
                  placeholder="2022"
                  type="number"
                  inputMode="numeric"
                  min={1960}
                  max={2026}
                  registerOptions={{
                    valueAsNumber: true,
                  }}
                />
              </div>
              <FormInput<RegisterFormInput>
                name={`cars.${index}.price_per_km`}
                label="Цена за 1 км"
                placeholder="3 рубля"
                type="number"
                inputMode="numeric"
                min={1}
                max={2026}
                registerOptions={{
                  valueAsNumber: true,
                }}
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <FormInput<RegisterFormInput>
                  name={`cars.${index}.license_plate`}
                  label="Номерной знак"
                  placeholder="1234 AB-7"
                />

                <FormInput<RegisterFormInput>
                  name={`cars.${index}.VIN`}
                  label="VIN"
                  placeholder="17 символов"
                />
              </div>

              <FormMediaInput<RegisterFormInput>
                name={`cars.${index}.photo`}
                label="Фотография автомобиля"
              />
            </div>
          </div>
        ))}

        <button
          type="button"
          onClick={handleAddCar}
          className="flex h-12 w-full items-center justify-center gap-2 rounded-xl border border-dashed border-gray-300 text-sm font-medium text-gray-600 transition-all hover:border-orange-400 hover:bg-orange-50/30 hover:text-orange-600"
        >
          <Plus className="size-4" />
          {fields.length > 0 ? 'Добавить ещё автомобиль' : 'Добавить автомобиль'}
        </button>

        {typeof carsError?.message === 'string' && (
          <span className="-mt-2 text-xs font-medium text-red-500">{carsError.message}</span>
        )}
      </div>
    </div>
  )
}

export default CarrierFields
