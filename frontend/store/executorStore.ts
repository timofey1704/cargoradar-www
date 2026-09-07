import { create } from 'zustand'

import type { Executor } from '@/types'

interface ExecutorStore {
  executor: Executor | null
  isAuthChecked: boolean

  setExecutor: (executor: Executor | null) => void
  setAuthChecked: (value: boolean) => void
  logout: () => void
}

/**
 * Приводит объект с API к форме, которую ждёт UI.
 * Бэкенд отдаёт вложенную подписку subscription.membership.name,
 * а компоненты читают плоское поле membership.
 */
function normalizeExecutor(executor: Executor): Executor {
  const membershipName = executor.subscription?.membership?.name

  return {
    ...executor,
    membership: membershipName || executor.membership,
  }
}

const useExecutorStore = create<ExecutorStore>(set => ({
  executor: null,
  isAuthChecked: false,

  setExecutor: executor => set({ executor: executor ? normalizeExecutor(executor) : null }),

  setAuthChecked: value => set({ isAuthChecked: value }),

  logout: () => set({ executor: null }),
}))

export default useExecutorStore
