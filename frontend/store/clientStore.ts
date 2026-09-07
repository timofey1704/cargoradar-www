import { create } from 'zustand'
import type { Client } from '@/types'

interface ClientStore {
  client: Client | null
  isAuthChecked: boolean

  setClient: (client: Client | null) => void
  setAuthChecked: (value: boolean) => void
  logout: () => void
  isLegal: () => boolean
  isIndividual: () => boolean
}

const useClientStore = create<ClientStore>((set, get) => ({
  client: null,
  isAuthChecked: false,

  setClient: client => set({ client }),

  setAuthChecked: value => set({ isAuthChecked: value }),

  logout: () =>
    set({
      client: null,
      isAuthChecked: false,
    }),

  // хелперы для удобной проверки типа
  isLegal: () => get().client?.type === 'legal',
  isIndividual: () => get().client?.type === 'individual',
}))

export default useClientStore
