'use client'

import { FormProvider } from 'react-hook-form'

import { FormInput } from '@/components/ui/form-input'
import { useAppForm } from '@/hooks/use-app-form'
import {
  loginSchema,
  type LoginFormInput,
} from '@/schemas/auth/login/loginSchema'

export default function LoginPage() {
  const {
    form,
    isVisible,
    togglePasswordVisibility,
  } = useAppForm({
    schema: loginSchema,

    defaultValues: {
      phone: '',
      password: '',
    },
  })

  return (
    <FormProvider {...form}>
      <form
        onSubmit={form.handleSubmit(async (values) => {
          await login(values)
        })}
      >
        <FormInput<LoginFormInput>
          name="phone"
          label="Ваш номер телефона"
          placeholder="+375 29 123-45-67"
          autoComplete="tel"
        />

        <FormInput<LoginFormInput>
          name="password"
          label="Ваш пароль"
          placeholder="Не менее 8 символов"
          autoComplete="current-password"
          isPassword
          isVisible={isVisible}
          togglePasswordVisibility={togglePasswordVisibility}
        />

        <button type="submit">
          Войти
        </button>
      </form>
    </FormProvider>
  )
}