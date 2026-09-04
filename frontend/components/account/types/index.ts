import type { Client } from '@/types/client'
import type { Executor } from '@/types/executor'

interface NavigationItem {
  name: string
  href: string
  icon: string
}

export type AccountSidebarProps =
  | {
      accountType: 'client'
      user: Client
      navigation: NavigationItem[]
    }
  | {
      accountType: 'executor'
      user: Executor
      navigation: NavigationItem[]
    }

export interface BurgerProps {
  navigation: NavigationItem[]
  accountType: 'client' | 'executor'
}
