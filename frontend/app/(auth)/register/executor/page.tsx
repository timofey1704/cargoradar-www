'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Check, Truck } from 'lucide-react'
import { FormProvider, useWatch } from 'react-hook-form'

import { FormInput } from '@/components/ui/form-input'
import { FormSelect } from '@/components/ui/form-select'
import { useAppForm } from '@/hooks/use-app-form'

import {
  ExecutorTypesNames,
  registerSchema,
  type RegisterFormInput,
} from '@/schemas/auth/register/executorSchema'
import { useRegister } from '@/hooks/use-register'
import { executorRegister } from '@/lib/auth/register'
import { objectToSelectOptions } from '@/lib/utils/select'
import CarrierFields from './components/CarrierFields'
import SupplierFields from './components/SupplierFields'
import ServiceFields from './components/ServiceFields'
import { Button } from '@/components/ui/button'

export default function RegisterPage() {
  const router = useRouter()

  const { form, isVisible, togglePasswordVisibility } = useAppForm({
    schema: registerSchema,

    defaultValues: {
      name: '',
      phone_number: '',
      email: '',
      password: '',
      type: 'carrier',
      cars: [],
      privacy_accepted: true,
    },
  })

  const accountType = useWatch({
    control: form.control,
    name: 'type',
  })

  useEffect(() => {
    if (accountType !== 'carrier') {
      form.setValue('cars', [], {
        shouldDirty: true,
        shouldValidate: false,
      })
    }

    if (accountType === 'service' || accountType === 'supplier') {
      const currentBrands = form.getValues('brands')

      if (!Array.isArray(currentBrands) || currentBrands.length === 0) {
        form.setValue('brands', ['all'], {
          shouldDirty: true,
          shouldValidate: true,
        })
      }
    }
  }, [accountType, form])

  const { mutate: register, isPending } = useRegister(executorRegister)

  const handleRegister = form.handleSubmit(values => {
    register(values, {
      onSuccess: () => {
        router.push('/executor')
      },
    })
  })

  return (
    <main className="min-h-screen bg-[#F7F7F5] px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-6xl items-center">
        <div className="grid w-full overflow-hidden rounded-4xl border border-black/5 bg-white shadow-[0_24px_80px_rgba(0,0,0,0.08)] lg:grid-cols-2">
          {/* Form */}
          <div className="flex items-center px-6 py-10 sm:px-10 lg:px-16 lg:py-12">
            <div className="mx-auto w-full max-w-md">
              <Link href="/" className="mb-8 inline-flex items-center gap-2">
                <div className="flex size-10 items-center justify-center rounded-xl bg-orange-500 text-white shadow-lg shadow-orange-500/20">
                  <Truck className="size-5" strokeWidth={2.2} />
                </div>

                <span className="text-xl font-bold tracking-tight text-gray-950">
                  Cargo<span className="text-orange-500">Radar</span>
                </span>
              </Link>

              <div className="mb-7">
                <p className="mb-2 text-sm font-medium text-orange-500">Регистрация исполнителя</p>

                <h1 className="text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
                  Создайте аккаунт
                </h1>

                <p className="mt-3 text-sm leading-6 text-gray-500">
                  Заполните данные, чтобы начать работать с заказами на CargoRadar.
                </p>
              </div>

              <FormProvider {...form}>
                <form onSubmit={handleRegister} className="flex flex-col gap-5">
                  <FormInput<RegisterFormInput>
                    name="name"
                    label="Ваше имя"
                    placeholder="Иван"
                    autoComplete="name"
                  />

                  <FormInput<RegisterFormInput>
                    name="phone_number"
                    label="Номер телефона"
                    placeholder="+375 29 123-45-67"
                    autoComplete="tel"
                    inputMode="tel"
                  />

                  <FormInput<RegisterFormInput>
                    name="email"
                    label="Email"
                    placeholder="example@mail.com"
                    type="email"
                    autoComplete="email"
                    inputMode="email"
                  />

                  <FormInput<RegisterFormInput>
                    name="password"
                    label="Пароль"
                    placeholder="Не менее 8 символов"
                    autoComplete="new-password"
                    isPassword
                    isVisible={isVisible}
                    togglePasswordVisibility={togglePasswordVisibility}
                  />

                  <FormSelect<RegisterFormInput>
                    name="type"
                    label="Тип аккаунта"
                    options={objectToSelectOptions(ExecutorTypesNames)}
                    placeholder="Выберите тип аккаунта"
                  />

                  {accountType === 'carrier' && <CarrierFields />}
                  {accountType === 'supplier' && <SupplierFields />}
                  {accountType === 'service' && <ServiceFields />}

                  {/* Privacy */}
                  <label className="flex cursor-pointer items-start gap-3">
                    <span className="relative mt-0.5 flex shrink-0">
                      <input
                        type="checkbox"
                        {...form.register('privacy_accepted')}
                        className="peer size-5 cursor-pointer appearance-none rounded-md border border-gray-300 transition-all checked:border-orange-500 checked:bg-orange-500 focus:ring-2 focus:ring-orange-500/20"
                      />

                      <Check className="pointer-events-none absolute inset-0 m-auto size-3.5 text-white opacity-0 transition-opacity peer-checked:opacity-100" />
                    </span>

                    <span className="text-xs leading-5 text-gray-500">
                      Я принимаю{' '}
                      <Link
                        href="/privacy"
                        className="font-medium text-gray-700 underline underline-offset-2 hover:text-orange-500"
                      >
                        политику конфиденциальности
                      </Link>{' '}
                      и условия использования сервиса.
                    </span>
                  </label>

                  {typeof form.formState.errors.privacy_accepted?.message === 'string' && (
                    <span className="-mt-3 text-xs font-medium text-red-500">
                      {form.formState.errors.privacy_accepted.message}
                    </span>
                  )}

                  <Button
                    disabled={form.formState.isSubmitting || isPending}
                    isSubmitting={isPending}
                    defaultText="Зарегистрироваться"
                    loadingText="Создаём аккаунт..."
                    showArrow={false}
                  />
                </form>
              </FormProvider>

              <p className="mt-7 text-center text-sm text-gray-500">
                Уже есть аккаунт?{' '}
                <Link
                  href="/login/executor"
                  className="font-semibold text-orange-500 transition-colors hover:text-orange-600 hover:underline"
                >
                  Войти
                </Link>
              </p>
            </div>
          </div>

          {/* Visual */}
          <div className="relative hidden overflow-hidden bg-gray-950 lg:block">
            <div className="absolute -top-32 -right-32 size-96 rounded-full bg-orange-500/20 blur-3xl" />
            <div className="absolute -bottom-32 -left-32 size-96 rounded-full bg-orange-400/10 blur-3xl" />

            <div className="relative flex h-full min-h-190 flex-col justify-between p-10 xl:p-14">
              <div>
                <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/70 backdrop-blur">
                  <span className="size-1.5 rounded-full bg-orange-400" />
                  CargoRadar
                </div>

                <h2 className="max-w-md text-3xl leading-tight font-bold tracking-tight text-white xl:text-4xl">
                  Всё необходимое для работы
                  <span className="text-orange-400"> в одном месте.</span>
                </h2>

                <p className="mt-5 max-w-sm text-sm leading-6 text-gray-400">
                  Получайте заказы, управляйте транспортом и контролируйте свои перевозки без лишней
                  рутины.
                </p>
              </div>

              {/* Registration preview */}
              <div className="relative mx-auto w-full max-w-md">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-2xl backdrop-blur-xl">
                  <div className="mb-5 flex items-center justify-between">
                    <span className="text-xs font-medium text-gray-400">ПРОФИЛЬ ИСПОЛНИТЕЛЯ</span>

                    <span className="rounded-full bg-orange-500/10 px-2.5 py-1 text-[10px] font-semibold text-orange-400">
                      НОВЫЙ
                    </span>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-[10px] font-medium tracking-wider text-gray-500 uppercase">
                        Тип аккаунта
                      </p>

                      <p className="mt-1 text-sm font-semibold text-white">Перевозчик</p>
                    </div>

                    <div className="border-t border-white/10 pt-4">
                      <p className="text-[10px] font-medium tracking-wider text-gray-500 uppercase">
                        Транспорт
                      </p>

                      <div className="mt-3 flex items-center gap-3">
                        <div className="flex size-10 items-center justify-center rounded-xl bg-orange-500/15 text-orange-400">
                          <Truck className="size-5" />
                        </div>

                        <div>
                          <p className="text-sm font-semibold text-white">MAN TGX</p>

                          <p className="text-xs text-gray-500">До 20 тонн · 82 м³</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 flex items-center gap-2 border-t border-white/10 pt-4">
                    <div className="flex size-6 items-center justify-center rounded-full bg-green-500/10">
                      <Check className="size-3 text-green-400" />
                    </div>

                    <span className="text-xs text-gray-400">Профиль готов к работе</span>
                  </div>
                </div>
              </div>

              <p className="text-xs text-gray-600">Перевозки становятся проще.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
