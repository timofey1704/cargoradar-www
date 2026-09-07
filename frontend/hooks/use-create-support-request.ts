'use client'

import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { SupportFormOutput } from '@/schemas/support/createRequest'

type CreateSupportRequestFunction = (values: SupportFormOutput) => Promise<unknown>

export function useCreateSupportRequest(
  createSupportRequestFunction: CreateSupportRequestFunction
) {
  return useMutation({
    mutationFn: createSupportRequestFunction,

    onError: error => {
      showToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Не удалось отправить заявку в поддержку',
      })
    },
  })
}
