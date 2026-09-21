'use client'

import { useEffect } from 'react'

import { useCurrentUser } from '@/hooks/use-current-user'
import { useCurrentExecutor } from '@/hooks/use-current-executor'
import useClientStore from '@/store/clientStore'
import useExecutorStore from '@/store/executorStore'

/**
 * Наполняет сторы клиента и исполнителя на публичных страницах, чтобы хедер
 * мог показать приветствие вместо кнопок входа.
 * Рендер детей не блокируется: как только /me отвечает, стор обновляется
 * и интерфейс перерисовывается.
 */
export default function SessionProvider({ children }: { children: React.ReactNode }) {
  const setClient = useClientStore(state => state.setClient)
  const setClientAuthChecked = useClientStore(state => state.setAuthChecked)
  const logoutClient = useClientStore(state => state.logout)

  const setExecutor = useExecutorStore(state => state.setExecutor)
  const setExecutorAuthChecked = useExecutorStore(state => state.setAuthChecked)
  const logoutExecutor = useExecutorStore(state => state.logout)

  const {
    data: client,
    isLoading: isClientLoading,
    isError: isClientError,
    error: clientError,
  } = useCurrentUser()

  const {
    data: executor,
    isLoading: isExecutorLoading,
    isError: isExecutorError,
    error: executorError,
  } = useCurrentExecutor()

  useEffect(() => {
    if (isClientLoading) return

    if (client) {
      setClient(client)
    } else if (
      isClientError &&
      clientError instanceof Error &&
      clientError.message === 'UNAUTHORIZED'
    ) {
      logoutClient()
    }

    setClientAuthChecked(true)
  }, [
    client,
    isClientLoading,
    isClientError,
    clientError,
    setClient,
    setClientAuthChecked,
    logoutClient,
  ])

  useEffect(() => {
    if (isExecutorLoading) return

    if (executor) {
      setExecutor(executor)
    } else if (
      isExecutorError &&
      executorError instanceof Error &&
      executorError.message === 'UNAUTHORIZED'
    ) {
      logoutExecutor()
    }

    setExecutorAuthChecked(true)
  }, [
    executor,
    isExecutorLoading,
    isExecutorError,
    executorError,
    setExecutor,
    setExecutorAuthChecked,
    logoutExecutor,
  ])

  return <>{children}</>
}
