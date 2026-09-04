import { FormInput } from '@/components/ui/form-input'
import { RegisterFormInput } from '@/schemas/auth/register/clientSchema'

const LegalFields = () => {
  return (
    <div className="mt-2 border-t border-gray-100 pt-6">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Контактные данные юр. лица</h3>
        <p className="mt-1 text-xs text-gray-500">Укажите юридические данные и адрес</p>
      </div>

      <div className="flex flex-col gap-4">
        <FormInput<RegisterFormInput>
          name="legal_name"
          label="Название юр. лица"
          placeholder="ООО «Пример»"
        />

        <FormInput<RegisterFormInput> name="UNP" label="УНП" placeholder="123456789" />

        <FormInput<RegisterFormInput>
          name="address"
          label="Адрес"
          placeholder="г. Минск, ул. ..."
        />
      </div>
    </div>
  )
}

export default LegalFields
