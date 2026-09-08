'use client'

import { FormProvider } from 'react-hook-form'

import { useAppForm } from '@/hooks/use-app-form'
import { FormInput } from '@/components/ui/form-input'
import { Button } from '@/components/ui/button'
import useClientStore from '@/store/clientStore'
import { useChangePersonalData } from '@/hooks/use-account-actions'
import { changeAccountData } from '@/lib/clientAccount/change-account-data'
import { useProfileImageUpload } from '@/hooks/use-profile-image-upload'
import showToast from '@/components/ui/toast'
import type { Client } from '@/types'

import PersonalDataSection from '@/components/account/profile/personal-data-section'
import NotificationsSection from '@/components/account/profile/notifications-section'
import CompanyDetailsSection from '@/components/account/profile/company-details-section'

import { profileSchema, type ProfileFormInput } from '@/schemas/account/profile/profileSchema'

const ProfilePage = () => {
  const { client, setClient } = useClientStore()
  const isLegalClient = client?.type === 'legal'

  const { mutateAsync: saveChanges, isPending } = useChangePersonalData(changeAccountData)

  const { form } = useAppForm({
    schema: profileSchema,
    defaultValues: {
      name: client?.name || '',
      phoneNumber: client?.phone_number || '',
      image: client?.image || '',
      email: client?.email || '',
      vinCode: client?.VIN_code || '',
      isNotificationsEnabled: client?.is_notifications_enabled ?? false,
      legalName: client?.type === 'legal' ? client.legal_name : '',
      unp: client?.type === 'legal' ? client.unp?.toString() : '',
      address: client?.type === 'legal' ? client.address : '',
    },
  })

  const { fileInputRef, previewUrl, handlePhotoChange, handleFileChange } = useProfileImageUpload({
    endpoint: `${process.env.NEXT_PUBLIC_API_URL}/account/profile/update-photo/`,
    currentImage: client?.image,
    onUploaded: image => client && setClient({ ...client, image }),
  })

  const handleSubmit = form.handleSubmit(async values => {
    const updated = await saveChanges(values)
    setClient(updated as Client)
    showToast({ type: 'success', message: 'Данные профиля обновлены!' })
  })

  return (
    <div className="space-y-8 pb-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Редактирование профиля</h1>
        <p className="mt-1 text-sm text-gray-500">
          Измените личные данные и настройки вашего аккаунта.
        </p>
      </div>

      <FormProvider {...form}>
        <form onSubmit={handleSubmit} className="space-y-6">
          <PersonalDataSection<ProfileFormInput>
            nameField="name"
            phoneField="phoneNumber"
            emailField="email"
            fileInputRef={fileInputRef}
            previewUrl={previewUrl}
            currentImage={client?.image}
            onPhotoChange={handlePhotoChange}
            onFileChange={handleFileChange}
            extraFields={
              <FormInput<ProfileFormInput>
                name="vinCode"
                label="VIN-код"
                placeholder="Введите VIN-код"
              />
            }
          />

          <NotificationsSection<ProfileFormInput> name="isNotificationsEnabled" />

          {isLegalClient && (
            <CompanyDetailsSection<ProfileFormInput>
              legalNameField="legalName"
              unpField="unp"
              addressField="address"
            />
          )}

          <div className="flex justify-end">
            <Button
              type="submit"
              variant="blue"
              size="lg"
              disabled={form.formState.isSubmitting || isPending}
              isSubmitting={isPending}
              loadingText="Сохраняем..."
            >
              Сохранить изменения
            </Button>
          </div>
        </form>
      </FormProvider>
    </div>
  )
}

export default ProfilePage
