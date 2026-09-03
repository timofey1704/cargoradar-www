'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FormProvider } from 'react-hook-form'
import { ArrowRight, MapPin, Package, Truck } from 'lucide-react'

import { FormInput } from '@/components/ui/form-input'
import { useAppForm } from '@/hooks/use-app-form'
import { loginSchema, type LoginFormInput } from '@/schemas/auth/login/loginSchema'
import { executorLogin } from '@/lib/auth/login'
import { useLogin } from '@/hooks/use-login'
import { Button } from '@/components/ui/button'

export default function ExecutorLoginPage() {
  const router = useRouter()
  const { form, isVisible, togglePasswordVisibility } = useAppForm({
    schema: loginSchema,
    defaultValues: {
      phone_number: '',
      password: '',
    },
  })

  const { mutate: login, isPending } = useLogin(executorLogin)

  const handleLogin = form.handleSubmit(values => {
    login(values, {
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
          <div className="flex items-center px-6 py-10 sm:px-10 lg:px-16 lg:py-14">
            <div className="mx-auto w-full max-w-md">
              {/* Logo */}
              <Link href="/" className="mb-10 inline-flex items-center gap-2">
                <div className="flex size-10 items-center justify-center rounded-xl bg-orange-500 text-white shadow-lg shadow-orange-500/20">
                  <Truck className="size-5" strokeWidth={2.2} />
                </div>

                <span className="text-xl font-bold tracking-tight text-gray-950">
                  Cargo<span className="text-orange-500">Radar</span>
                </span>
              </Link>

              <div className="mb-8">
                <p className="mb-2 text-sm font-medium text-orange-500">
                  Личный кабинет исполнителя
                </p>

                <h1 className="text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
                  С возвращением!
                </h1>

                <p className="mt-3 text-sm leading-6 text-gray-500">
                  Войдите в аккаунт, чтобы находить заказы и управлять своими перевозками.
                </p>
              </div>

              <FormProvider {...form}>
                <form onSubmit={handleLogin} className="flex flex-col gap-5">
                  <FormInput<LoginFormInput>
                    name="phone_number"
                    label="Номер телефона"
                    placeholder="+375 29 123-45-67"
                    autoComplete="tel"
                    inputMode="tel"
                  />

                  <div>
                    <FormInput<LoginFormInput>
                      name="password"
                      label="Пароль"
                      placeholder="Введите пароль"
                      autoComplete="current-password"
                      isPassword
                      isVisible={isVisible}
                      togglePasswordVisibility={togglePasswordVisibility}
                    />

                    <div className="mt-2 flex justify-end">
                      <Link
                        href="/password-recovery"
                        className="text-sm font-medium text-gray-500 transition-colors hover:text-orange-500"
                      >
                        Забыли пароль?
                      </Link>
                    </div>
                  </div>

                  <Button
                    disabled={form.formState.isSubmitting || isPending}
                    isSubmitting={isPending}
                    defaultText="Войти"
                    loadingText="Входим..."
                    showArrow={false}
                  />
                </form>
              </FormProvider>

              <div className="my-8 flex items-center gap-4">
                <div className="h-px flex-1 bg-gray-200" />

                <span className="text-xs font-medium text-gray-400">ИЛИ</span>

                <div className="h-px flex-1 bg-gray-200" />
              </div>

              <p className="text-center text-sm text-gray-500">
                Ещё не зарегистрированы?{' '}
                <Link
                  href="register/executor"
                  className="font-semibold text-orange-500 transition-colors hover:text-orange-600 hover:underline"
                >
                  Создать аккаунт
                </Link>
              </p>

              <div className="mt-8 border-t border-gray-100 pt-6 text-center">
                <Link
                  href="/login/client"
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-400 transition-colors hover:text-gray-700"
                >
                  Вы клиент?
                  <span className="text-gray-600">Войти как клиент</span>
                  <ArrowRight className="size-3.5" />
                </Link>
              </div>
            </div>
          </div>

          {/* Carrier visual */}
          <div className="relative hidden overflow-hidden bg-gray-950 lg:block">
            <div className="absolute -top-32 -right-32 size-96 rounded-full bg-orange-500/20 blur-3xl" />
            <div className="absolute -bottom-32 -left-32 size-96 rounded-full bg-orange-400/10 blur-3xl" />

            <div className="relative flex h-full min-h-170 flex-col justify-between p-10 xl:p-14">
              <div>
                <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/70 backdrop-blur">
                  <span className="size-1.5 rounded-full bg-orange-400" />
                  Для исполнителей
                </div>

                <h2 className="max-w-md text-3xl leading-tight font-bold tracking-tight text-white xl:text-4xl">
                  Находите новые
                  <span className="text-orange-400"> заказы на перевозку.</span>
                </h2>

                <p className="mt-5 max-w-sm text-sm leading-6 text-gray-400">
                  Выбирайте подходящие маршруты, управляйте заказами и развивайте свой бизнес вместе
                  с CargoRadar.
                </p>
              </div>

              {/* Order card */}
              <div className="relative mx-auto w-full max-w-md">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-2xl backdrop-blur-xl">
                  <div className="mb-5 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="flex size-8 items-center justify-center rounded-lg bg-orange-500/15 text-orange-400">
                        <Package className="size-4" />
                      </div>

                      <div>
                        <p className="text-xs font-semibold text-white">Новый заказ</p>
                        <p className="text-[10px] text-gray-500">Только что</p>
                      </div>
                    </div>

                    <span className="rounded-full bg-green-400/10 px-2.5 py-1 text-[10px] font-semibold text-green-400">
                      ДОСТУПЕН
                    </span>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex flex-col items-center pt-1">
                      <div className="flex size-8 items-center justify-center rounded-full bg-orange-500/15 text-orange-400">
                        <MapPin className="size-4" />
                      </div>

                      <div className="my-1 w-px flex-1 border-l border-dashed border-gray-600" />

                      <div className="size-2 rounded-full bg-gray-500" />
                    </div>

                    <div className="flex flex-1 flex-col gap-6">
                      <div>
                        <p className="text-[10px] font-medium tracking-wider text-gray-500 uppercase">
                          Откуда
                        </p>

                        <p className="mt-1 text-sm font-semibold text-white">Минск</p>
                      </div>

                      <div>
                        <p className="text-[10px] font-medium tracking-wider text-gray-500 uppercase">
                          Куда
                        </p>

                        <p className="mt-1 text-sm font-semibold text-white">Гродно</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3 border-t border-white/10 pt-4">
                    <div>
                      <p className="text-[10px] text-gray-500">Вес</p>

                      <p className="mt-1 text-xs font-medium text-gray-300">12 тонн</p>
                    </div>

                    <div>
                      <p className="text-[10px] text-gray-500">Тип кузова</p>

                      <p className="mt-1 text-xs font-medium text-gray-300">Тент</p>
                    </div>
                  </div>
                </div>

                {/* Floating status */}
                <div className="absolute -right-5 -bottom-6 flex items-center gap-3 rounded-2xl border border-white/10 bg-gray-900 px-4 py-3 shadow-xl">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-orange-500">
                    <Truck className="size-4 text-white" />
                  </div>

                  <div>
                    <p className="text-[10px] text-gray-500">Ваш транспорт</p>

                    <p className="text-xs font-semibold text-white">Готов к работе</p>
                  </div>
                </div>
              </div>

              <p className="text-xs text-gray-600">Больше заказов. Меньше простоя.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
