'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'

import useClientStore from '@/store/clientStore'
import useExecutorStore from '@/store/executorStore'

import { clientLogout, executorLogout } from '@/lib/auth/logout'

type LogoutRole = 'client' | 'executor'

export function useLogout(role: LogoutRole) {
  const queryClient = useQueryClient()

  const clientLogoutStore = useClientStore(state => state.logout)
  const executorLogoutStore = useExecutorStore(state => state.logout)

  const mutation = useMutation({
    mutationFn: async () => {
      if (role === 'client') {
        return clientLogout()
      }

      return executorLogout()
    },

    onSuccess: async () => {
      await queryClient.clear()

      if (role === 'client') {
        clientLogoutStore()
      } else {
        executorLogoutStore()
      }
    },
  })

  return {
    logout: mutation.mutate,
    logoutAsync: mutation.mutateAsync,
    isLoggingOut: mutation.isPending,
    error: mutation.error,
  }
}

// пример использования

// const {
//   logout,
//   isLoggingOut,
// } = useLogout('client')

// <button
//   type="button"
//   onClick={() => logout()}
//   disabled={isLoggingOut}
// >
//   {isLoggingOut ? 'Выход...' : 'Выйти'}
// </button>
