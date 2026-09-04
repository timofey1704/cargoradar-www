'use client'

import { useEffect } from 'react'
import { useCurrentUser } from '@/hooks/use-current-user'
import useClientStore from '@/store/clientStore'

export default function ClientAuthProvider({ children }: { children: React.ReactNode }) {
  const { setClient, setAuthChecked, logout } = useClientStore()

  const { data: client, isLoading, isError, error } = useCurrentUser()

  useEffect(() => {
    console.log(
      '[ClientAuthProvider] effect: isLoading=%s client=%s isError=%s error=%s',
      isLoading,
      client ? `yes(id=${client.id})` : 'no',
      isError,
      error instanceof Error ? JSON.stringify(error.message) : 'null',
    )

    if (isLoading) return

    if (client) {
      setClient(client)
    } else if (isError && error instanceof Error && error.message === 'UNAUTHORIZED') {
      logout()
    }

    setAuthChecked(true)
  }, [client, isLoading, isError, error, setClient, setAuthChecked, logout])

  if (isLoading) {
    return null
  }

  return <>{children}</>
}
