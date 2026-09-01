'use client'

import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { LoginFormOutput } from '@/schemas/auth/login/loginSchema'

type RegisterFunction = (values: LoginFormOutput) => Promise<unknown>

export function useRegister(registerFunction: RegisterFunction) {
  return useMutation({
    mutationFn: registerFunction,

    onError: error => {
      showToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Не удалось выполнить регистрацию',
      })
    },
  })
}
