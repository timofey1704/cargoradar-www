import { FormInput } from '@/components/ui/form-input'
import { FormMultiSelect } from '@/components/ui/form-multi-select'
import type { RegisterFormInput } from '@/schemas/auth/register/executorSchema'
import { BRAND_OPTIONS } from '@/app/(auth)/register/executor/utils/carBrandOptions'

const SupplierFields = () => {
  return (
    <div className="mt-2 border-t border-gray-100 pt-6">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Реквизиты поставщика</h3>
        <p className="mt-1 text-xs text-gray-500">Укажите юридические данные и точку выдачи</p>
      </div>

      <div className="flex flex-col gap-4">
        <FormInput<RegisterFormInput>
          name="legal_name"
          label="Название юр. лица"
          placeholder="ООО «Пример»"
        />

        <FormInput<RegisterFormInput> name="UNP" label="УНП" placeholder="123456789" />

        <FormInput<RegisterFormInput>
          name="pickup_point"
          label="Точка выдачи"
          placeholder="г. Минск, ул. ..."
        />
        <FormMultiSelect<RegisterFormInput>
          name="brands"
          label="Марки автомобилей"
          placeholder="Выберите марки"
          options={BRAND_OPTIONS}
        />
      </div>
    </div>
  )
}

export default SupplierFields
