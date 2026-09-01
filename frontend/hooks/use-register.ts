'use client'

import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { RegisterFormOutput as ClientRegisterFormOutput } from '@/schemas/auth/register/clientSchema'
import type { RegisterFormOutput as ExecutorRegisterFormOutput } from '@/schemas/auth/register/executorSchema'

type RegisterFormOutput = ClientRegisterFormOutput | ExecutorRegisterFormOutput

type RegisterFunction = (values: RegisterFormOutput) => Promise<unknown>

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
