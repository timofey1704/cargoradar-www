import { useQuery } from '@tanstack/react-query'
import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { SupportFormOutput } from '@/schemas/support/createRequest'

import { clientRequest } from '@/lib/support/get-requests'
import type { SupportTicket } from '@/types/index'

type CreateSupportRequestFunction = (values: SupportFormOutput) => Promise<unknown>

export function useSupportRequests() {
  return useQuery<SupportTicket[]>({
    queryKey: ['support-requests'],
    queryFn: clientRequest,
    retry: false,
  })
}

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
