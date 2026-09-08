'use client'

import { FormProvider } from 'react-hook-form'

import { useAppForm } from '@/hooks/use-app-form'
import { useExecutorChangePersonalData } from '@/hooks/use-account-actions'
import useExecutorStore from '@/store/executorStore'
import { Button } from '@/components/ui/button'
import showToast from '@/components/ui/toast'

import PersonalDataSection from '@/components/account/profile/personal-data-section'
import NotificationsSection from '@/components/account/profile/notifications-section'
import CompanyDetailsSection from '@/components/account/profile/company-details-section'

import { changeAccountData } from '@/lib/executorAccount/change-account-data'
import { useProfileImageUpload } from '@/hooks/use-profile-image-upload'
import { getEditProfileDefaultValues } from '@/lib/utils/edit-profile-defaults'

import type { Executor } from '@/types'
import {
  editProfileSchema,
  type EditProfileFormInput,
} from '@/schemas/executor/profile/profileSchema'

const ProfilePage = () => {
  const { executor, setExecutor } = useExecutorStore()

  const { mutateAsync: saveChanges, isPending } = useExecutorChangePersonalData(changeAccountData)

  const { form } = useAppForm({
    schema: editProfileSchema,
    defaultValues: getEditProfileDefaultValues(executor),
  })

  const { fileInputRef, previewUrl, handlePhotoChange, handleFileChange } = useProfileImageUpload({
    endpoint: `${process.env.NEXT_PUBLIC_API_URL}/executor/profile/update-photo/`,
    currentImage: executor?.image,
    onUploaded: image => executor && setExecutor({ ...executor, image }),
  })

  const handleSubmit = form.handleSubmit(async values => {
    const updated = await saveChanges(values)
    setExecutor(updated as Executor)
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
          <PersonalDataSection<EditProfileFormInput>
            nameField="name"
            phoneField="phone_number"
            emailField="email"
            fileInputRef={fileInputRef}
            previewUrl={previewUrl}
            currentImage={executor?.image}
            onPhotoChange={handlePhotoChange}
            onFileChange={handleFileChange}
          />

          <NotificationsSection<EditProfileFormInput> name="isNotificationsEnabled" />

          {(executor?.type === 'supplier' || executor?.type === 'service') && (
            <CompanyDetailsSection<EditProfileFormInput>
              legalNameField="legal_name"
              unpField="UNP"
              addressField="address"
              brandsField="brands"
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
