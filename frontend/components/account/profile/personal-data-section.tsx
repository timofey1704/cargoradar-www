import type { ChangeEvent, ReactNode, RefObject } from 'react'
import type { FieldValues, Path } from 'react-hook-form'

import { FormInput } from '@/components/ui/form-input'
import AvatarUploadField from '@/components/account/profile/avatar-upload-field'

interface PersonalDataSectionProps<T extends FieldValues> {
  nameField: Path<T>
  phoneField: Path<T>
  emailField: Path<T>
  fileInputRef: RefObject<HTMLInputElement | null>
  previewUrl: string
  currentImage?: string
  onPhotoChange: () => void
  onFileChange: (e: ChangeEvent<HTMLInputElement>) => void
  extraFields?: ReactNode
}

function PersonalDataSection<T extends FieldValues>({
  nameField,
  phoneField,
  emailField,
  fileInputRef,
  previewUrl,
  currentImage,
  onPhotoChange,
  onFileChange,
  extraFields,
}: PersonalDataSectionProps<T>) {
  return (
    <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-6 py-5">
        <h2 className="text-lg font-semibold text-gray-900">Личные данные</h2>
        <p className="mt-1 text-sm text-gray-500">Основная информация вашего аккаунта.</p>
      </div>

      <div className="space-y-6 p-6">
        <AvatarUploadField
          fileInputRef={fileInputRef}
          previewUrl={previewUrl}
          currentImage={currentImage}
          onPhotoChange={onPhotoChange}
          onFileChange={onFileChange}
        />

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <FormInput<T> name={nameField} label="Имя" placeholder="Введите имя" />
          <FormInput<T> name={phoneField} label="Телефон" placeholder="+375 (__) ___-__-__" />
        </div>

        <FormInput<T> name={emailField} label="Email" type="email" placeholder="Введите email" />

        {extraFields}
      </div>
    </section>
  )
}

export default PersonalDataSection
