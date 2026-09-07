import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { LoginFormOutput } from '@/schemas/auth/login/loginSchema'

type LoginFunction = (values: LoginFormOutput) => Promise<unknown>

export function useLogin(loginFunction: LoginFunction) {
  return useMutation({
    mutationFn: loginFunction,

    onError: error => {
      showToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Не удалось выполнить вход',
      })
    },
  })
}
