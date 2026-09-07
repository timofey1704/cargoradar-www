import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { ProfileFormOutput } from '@/schemas/account/profile/profileSchema'

type ChangeAccountData = (values: ProfileFormOutput) => Promise<unknown>

export function useChangePersonalData(changeDataFunction: ChangeAccountData) {
  return useMutation({
    mutationFn: changeDataFunction,

    onError: error => {
      showToast({
        type: 'error',
        message:
          error instanceof Error ? error.message : 'Не удалось выполнить сохранение данных',
      })
    },
  })
}
