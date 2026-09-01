'use client'

import { useEffect } from 'react'

import { useCurrentExecutor } from '@/hooks/use-current-executor'
import useExecutorStore from '@/store/executorStore'

export default function ExecutorAuthProvider({ children }: { children: React.ReactNode }) {
  const { setExecutor, setAuthChecked, logout } = useExecutorStore()

  const { data: executor, isLoading, isError, error } = useCurrentExecutor()

  useEffect(() => {
    if (isLoading) return

    if (executor) {
      setExecutor(executor)
    } else if (isError && error instanceof Error && error.message === 'UNAUTHORIZED') {
      logout()
    }

    setAuthChecked(true)
  }, [executor, isLoading, isError, error, setExecutor, setAuthChecked, logout])

  if (isLoading) {
    return null
  }

  return <>{children}</>
}
