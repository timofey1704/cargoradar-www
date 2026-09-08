import { useMutation } from '@tanstack/react-query'
import showToast from '@/components/ui/toast'
import type { ProfileFormOutput } from '@/schemas/account/profile/profileSchema'
import type { EditProfileFormOutput } from '@/schemas/executor/profile/profileSchema'

type ChangeAccountData = (values: ProfileFormOutput) => Promise<unknown>
type ChangeExecutorAccountData = (values: EditProfileFormOutput) => Promise<unknown>

export function useChangePersonalData(changeDataFunction: ChangeAccountData) {
  return useMutation({
    mutationFn: changeDataFunction,

    onError: error => {
      showToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Не удалось выполнить сохранение данных',
      })
    },
  })
}

export function useExecutorChangePersonalData(changeDataFunction: ChangeExecutorAccountData) {
  return useMutation({
    mutationFn: changeDataFunction,

    onError: error => {
      showToast({
        type: 'error',
        message: error instanceof Error ? error.message : 'Не удалось выполнить сохранение данных',
      })
    },
  })
}
