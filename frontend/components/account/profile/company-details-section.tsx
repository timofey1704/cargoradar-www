import type { FieldValues, Path } from 'react-hook-form'

import { FormInput } from '@/components/ui/form-input'
import { FormMultiSelect } from '@/components/ui/form-multi-select'
import { BRAND_OPTIONS } from '@/app/(auth)/register/executor/utils/carBrandOptions'

interface CompanyDetailsSectionProps<T extends FieldValues> {
  legalNameField: Path<T>
  unpField: Path<T>
  addressField: Path<T>
  brandsField?: Path<T>
}

function CompanyDetailsSection<T extends FieldValues>({
  legalNameField,
  unpField,
  addressField,
  brandsField,
}: CompanyDetailsSectionProps<T>) {
  return (
    <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-6 py-5">
        <h2 className="text-lg font-semibold text-gray-900">Данные организации</h2>
        <p className="mt-1 text-sm text-gray-500">Реквизиты юридического лица.</p>
      </div>

      <div className="space-y-5 p-6">
        <FormInput<T>
          name={legalNameField}
          label="Название юридического лица"
          placeholder='Например, ООО "Название"'
        />

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <FormInput<T> name={unpField} label="УНП" placeholder="Введите УНП" />
          <FormInput<T> name={addressField} label="Адрес" placeholder="Введите юридический адрес" />

          {brandsField && (
            <FormMultiSelect<T>
              name={brandsField}
              label="Марки автомобилей"
              placeholder="Выберите марки"
              options={BRAND_OPTIONS}
            />
          )}
        </div>
      </div>
    </section>
  )
}

export default CompanyDetailsSection
