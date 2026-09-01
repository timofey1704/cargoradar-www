'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FormProvider } from 'react-hook-form'
import { ArrowRight, Check, ShieldCheck, Truck, UserPlus } from 'lucide-react'

import { FormInput } from '@/components/ui/form-input'
import { useAppForm } from '@/hooks/use-app-form'
import { registerSchema, type RegisterFormInput } from '@/schemas/auth/register/clientSchema'
import { useRegister } from '@/hooks/use-register'
import { clientRegister } from '@/lib/auth/register'
import { Button } from '@/components/ui/button'

const benefits = [
  'Создавайте заявки на перевозку',
  'Находите подходящих исполнителей',
  'Контролируйте перевозки в одном месте',
]

export default function ClientRegisterPage() {
  const router = useRouter()
  const { form } = useAppForm({
    schema: registerSchema,
    defaultValues: {
      name: '',
      email: '',
      phone_number: '',
      password: '',
      privacy_accepted: true,
    },
  })

  const { mutate: register, isPending } = useRegister(clientRegister)

  const handleRegister = form.handleSubmit(values => {
    register(values, {
      onSuccess: () => {
        router.push('/account')
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
              {/* Logo */}
              <Link href="/" className="mb-8 inline-flex items-center gap-2">
                <div className="flex size-10 items-center justify-center rounded-xl bg-orange-500 text-white shadow-lg shadow-orange-500/20">
                  <Truck className="size-5" strokeWidth={2.2} />
                </div>

                <span className="text-xl font-bold tracking-tight text-gray-950">
                  Cargo<span className="text-orange-500">Radar</span>
                </span>
              </Link>

              {/* Heading */}
              <div className="mb-7">
                <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-orange-50 px-3 py-1.5 text-xs font-semibold text-orange-600">
                  <UserPlus className="size-3.5" />
                  Регистрация клиента
                </div>

                <h1 className="text-3xl font-bold tracking-tight text-gray-950 sm:text-4xl">
                  Создайте аккаунт
                </h1>

                <p className="mt-3 text-sm leading-6 text-gray-500">
                  Зарегистрируйтесь, чтобы создавать заявки и находить исполнителей для своих
                  грузоперевозок.
                </p>
              </div>

              <FormProvider {...form}>
                <form onSubmit={handleRegister} className="flex flex-col gap-4">
                  <FormInput<RegisterFormInput>
                    name="name"
                    label="Ваше имя"
                    placeholder="Иван Иванов"
                    autoComplete="name"
                  />

                  <FormInput<RegisterFormInput>
                    name="email"
                    label="Email"
                    type="email"
                    placeholder="ivan@example.com"
                    autoComplete="email"
                    inputMode="email"
                  />

                  <FormInput<RegisterFormInput>
                    name="phone_number"
                    label="Номер телефона"
                    placeholder="+375 29 123-45-67"
                    autoComplete="tel"
                    inputMode="tel"
                  />

                  <FormInput<RegisterFormInput>
                    name="password"
                    label="Пароль"
                    placeholder="Не менее 8 символов"
                    autoComplete="new-password"
                    isPassword
                  />

                  {/* Privacy */}
                  <label className="mt-1 flex cursor-pointer items-start gap-3">
                    <input
                      type="checkbox"
                      {...form.register('privacy_accepted')}
                      className="mt-0.5 size-4 shrink-0 cursor-pointer rounded border-gray-300 text-orange-500 accent-orange-500 focus:ring-orange-500"
                    />

                    <span className="text-xs leading-5 text-gray-500">
                      Я принимаю{' '}
                      <Link
                        href="/privacy"
                        className="font-medium text-gray-700 underline underline-offset-2 transition-colors hover:text-orange-500"
                      >
                        политику конфиденциальности
                      </Link>{' '}
                      и условия использования сервиса.
                    </span>
                  </label>

                  {/* Submit */}
                  <Button
                    disabled={form.formState.isSubmitting || isPending}
                    isSubmitting={isPending}
                    defaultText="Зарегистрироваться"
                    loadingText="Создаём аккаунт..."
                    showArrow={false}
                  />
                </form>
              </FormProvider>

              {/* Login */}
              <div className="my-7 flex items-center gap-4">
                <div className="h-px flex-1 bg-gray-200" />

                <span className="text-xs font-medium text-gray-400">УЖЕ ЕСТЬ АККАУНТ?</span>

                <div className="h-px flex-1 bg-gray-200" />
              </div>

              <p className="text-center text-sm text-gray-500">
                <Link
                  href="/login/client"
                  className="font-semibold text-orange-500 transition-colors hover:text-orange-600 hover:underline"
                >
                  Войти в аккаунт
                </Link>
              </p>

              {/* Executor */}
              <div className="mt-7 border-t border-gray-100 pt-5 text-center">
                <Link
                  href="/register/executor"
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-400 transition-colors hover:text-gray-700"
                >
                  Вы исполнитель?
                  <span className="text-gray-600">Зарегистрироваться как исполнитель</span>
                  <ArrowRight className="size-3.5" />
                </Link>
              </div>
            </div>
          </div>

          {/* Visual */}
          <div className="relative hidden overflow-hidden bg-gray-950 lg:block">
            {/* Decorative gradients */}
            <div className="absolute -top-32 -right-32 size-96 rounded-full bg-orange-500/20 blur-3xl" />
            <div className="absolute -bottom-40 -left-32 size-96 rounded-full bg-orange-400/10 blur-3xl" />

            <div className="relative flex h-full min-h-180 flex-col justify-between p-10 xl:p-14">
              <div>
                <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/70 backdrop-blur">
                  <span className="size-1.5 rounded-full bg-orange-400" />
                  CargoRadar
                </div>

                <h2 className="max-w-md text-3xl leading-tight font-bold tracking-tight text-white xl:text-4xl">
                  Перевозки становятся
                  <span className="text-orange-400"> проще.</span>
                </h2>

                <p className="mt-5 max-w-sm text-sm leading-6 text-gray-400">
                  Один аккаунт для управления грузоперевозками — от создания заявки до завершения
                  заказа.
                </p>
              </div>

              {/* Benefits */}
              <div className="relative mx-auto w-full max-w-md">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-xl">
                  <p className="mb-5 text-xs font-medium tracking-wider text-gray-500 uppercase">
                    Всё необходимое в одном месте
                  </p>

                  <div className="flex flex-col gap-5">
                    {benefits.map((benefit, index) => (
                      <div key={benefit} className="flex items-center gap-4">
                        <div className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-orange-500/15 text-orange-400">
                          <Check className="size-4" strokeWidth={2.5} />
                        </div>

                        <div>
                          <p className="text-sm font-medium text-white">{benefit}</p>

                          <p className="mt-0.5 text-xs text-gray-500">
                            {index === 0 && 'Быстро оформляйте новые перевозки'}
                            {index === 1 && 'Выбирайте подходящих перевозчиков'}
                            {index === 2 && 'Следите за статусом заказа'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Floating security card */}
                <div className="absolute -right-5 -bottom-6 flex items-center gap-3 rounded-2xl border border-white/10 bg-gray-900 px-4 py-3 shadow-xl">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-green-500/10">
                    <ShieldCheck className="size-4 text-green-400" />
                  </div>

                  <div>
                    <p className="text-[10px] text-gray-500">Ваши данные</p>
                    <p className="text-xs font-semibold text-white">Под надёжной защитой</p>
                  </div>
                </div>
              </div>

              <p className="text-xs text-gray-600">CargoRadar — платформа для грузоперевозок.</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
