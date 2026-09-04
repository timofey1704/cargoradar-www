import { FormInput } from '@/components/ui/form-input'
import { FormMultiSelect } from '@/components/ui/form-multi-select'
import { CAR_BRAND_NAMES } from '@/consts/carBrands'
import type { RegisterFormInput } from '@/schemas/auth/register/executorSchema'

export const SERVICE_BRAND_OPTIONS = Object.entries(CAR_BRAND_NAMES).map(([value, label]) => ({
  value,
  label,
}))

const ServiceFields = () => {
  return (
    <div className="mt-2 border-t border-gray-100 pt-6">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Данные СТО</h3>
        <p className="mt-1 text-xs text-gray-500">Укажите реквизиты и адрес станции</p>
      </div>

      <div className="flex flex-col gap-4">
        <FormInput<RegisterFormInput>
          name="legal_name"
          label="Название юр. лица"
          placeholder="ООО «Пример»"
        />

        <FormInput<RegisterFormInput> name="UNP" label="УНП" placeholder="123456789" />

        <FormInput<RegisterFormInput>
          name="service_address"
          label="Адрес СТО"
          placeholder="г. Минск, ул. Примерная, д. 1"
        />

        <FormMultiSelect<RegisterFormInput>
          name="brands"
          label="Марки автомобилей"
          placeholder="Выберите марки"
          options={SERVICE_BRAND_OPTIONS}
        />
      </div>
    </div>
  )
}

export default ServiceFields
