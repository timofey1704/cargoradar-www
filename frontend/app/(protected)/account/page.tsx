'use client'

import { FormProvider } from 'react-hook-form'
import { Bell, Camera, User } from 'lucide-react'

import { useAppForm } from '@/hooks/use-app-form'
import { FormInput } from '@/components/ui/form-input'
import { Button } from '@/components/ui/button'
import useClientStore from '@/store/clientStore'
import { useChangePersonalData } from '@/hooks/use-account-actions'
import { changeAccountData } from '@/lib/clientAccount/change-account-data'
import showToast from '@/components/ui/toast'
import type { Client } from '@/types'

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
      email: client?.email || '',
      vinCode: client?.VIN_code || '',
      isNotificationsEnabled: client?.is_notifications_enabled ?? false,
      legalName: client?.type === 'legal' ? client.legal_name : '',
      unp: client?.type === 'legal' ? client.unp?.toString() : '',
      address: client?.type === 'legal' ? client.address : '',
    },
  })

  const handleSubmit = form.handleSubmit(async values => {
    const updated = await saveChanges(values)

    // бэкенд возвращает свежий ClientRead — кладём его в стор,
    // чтобы и профиль, и юрданные обновились в UI.
    setClient(updated as Client)

    showToast({ type: 'success', message: 'Данные профиля обновлены!' })
  })

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Редактирование профиля</h1>

        <p className="mt-1 text-sm text-gray-500">
          Измените личные данные и настройки вашего аккаунта.
        </p>
      </div>

      <FormProvider {...form}>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal data */}
          <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
            <div className="border-b border-gray-100 px-6 py-5">
              <h2 className="text-lg font-semibold text-gray-900">Личные данные</h2>

              <p className="mt-1 text-sm text-gray-500">Основная информация вашего аккаунта.</p>
            </div>

            <div className="space-y-6 p-6">
              {/* Avatar */}
              <div className="flex items-center gap-5">
                <div className="relative flex size-20 shrink-0 items-center justify-center overflow-hidden rounded-full bg-gray-100">
                  <User className="size-8 text-gray-400" />

                  <button
                    type="button"
                    className="absolute inset-0 flex items-center justify-center bg-black/0 text-white opacity-0 transition-all hover:bg-black/40 hover:opacity-100"
                  >
                    <Camera className="size-5" />
                  </button>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-900">Изображение профиля</p>

                  <p className="mt-1 text-xs text-gray-500">JPG или PNG, размер файла до 5 МБ.</p>

                  <button
                    type="button"
                    className="mt-2 text-sm font-medium text-orange-500 transition-colors hover:text-orange-600"
                  >
                    Изменить фото
                  </button>
                </div>
              </div>

              {/* Fields */}
              <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                <FormInput<ProfileFormInput> name="name" label="Имя" placeholder="Введите имя" />

                <FormInput<ProfileFormInput>
                  name="phoneNumber"
                  label="Телефон"
                  placeholder="+375 (__) ___-__-__"
                />
              </div>

              <FormInput<ProfileFormInput>
                name="email"
                label="Email"
                type="email"
                placeholder="Введите email"
              />

              <FormInput<ProfileFormInput>
                name="vinCode"
                label="VIN-код"
                placeholder="Введите VIN-код"
              />
            </div>
          </section>

          {/* Notifications */}
          <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
            <div className="border-b border-gray-100 px-6 py-5">
              <h2 className="text-lg font-semibold text-gray-900">Настройки</h2>

              <p className="mt-1 text-sm text-gray-500">Управляйте настройками вашего аккаунта.</p>
            </div>

            <div className="p-6">
              <label className="flex cursor-pointer items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex size-10 items-center justify-center rounded-xl bg-gray-50">
                    <Bell className="size-5 text-gray-500" />
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-900">Получать уведомления</p>

                    <p className="mt-0.5 text-xs text-gray-500">
                      Уведомления о заказах и важных событиях.
                    </p>
                  </div>
                </div>

                <input
                  type="checkbox"
                  {...form.register('isNotificationsEnabled')}
                  className="size-5 accent-orange-500"
                />
              </label>
            </div>
          </section>

          {/* Legal client */}
          {isLegalClient && (
            <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
              <div className="border-b border-gray-100 px-6 py-5">
                <h2 className="text-lg font-semibold text-gray-900">Данные организации</h2>

                <p className="mt-1 text-sm text-gray-500">Реквизиты юридического лица.</p>
              </div>

              <div className="space-y-5 p-6">
                <FormInput<ProfileFormInput>
                  name="legalName"
                  label="Название юридического лица"
                  placeholder='Например, ООО "Название"'
                />

                <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                  <FormInput<ProfileFormInput> name="unp" label="УНП" placeholder="Введите УНП" />

                  <FormInput<ProfileFormInput>
                    name="address"
                    label="Адрес"
                    placeholder="Введите юридический адрес"
                  />
                </div>
              </div>
            </section>
          )}

          {/* Actions */}
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
