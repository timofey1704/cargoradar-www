import { create } from 'zustand'

import type { Executor } from '@/types'

interface ExecutorStore {
  executor: Executor | null
  isAuthChecked: boolean

  setExecutor: (executor: Executor | null) => void
  setAuthChecked: (value: boolean) => void
  logout: () => void
}

const useExecutorStore = create<ExecutorStore>(set => ({
  executor: null,
  isAuthChecked: false,

  setExecutor: executor => set({ executor }),

  setAuthChecked: value => set({ isAuthChecked: value }),

  logout: () => set({ executor: null }),
}))

export default useExecutorStore
