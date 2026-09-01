import { create } from 'zustand'

import type { Client } from '@/types'

interface ClientStore {
  client: Client | null
  isAuthChecked: boolean

  setClient: (client: Client | null) => void
  setAuthChecked: (value: boolean) => void
  logout: () => void
}

const useClientStore = create<ClientStore>(set => ({
  client: null,
  isAuthChecked: false,

  setClient: client => set({ client }),

  setAuthChecked: value => set({ isAuthChecked: value }),

  logout: () => set({ client: null }),
}))

export default useClientStore
