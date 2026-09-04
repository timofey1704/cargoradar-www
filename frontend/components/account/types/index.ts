import type { LucideIcon } from 'lucide-react'
import type { Client } from '@/types/client'
import type { Executor } from '@/types/executor'

export interface NavigationItem {
  name: string
  href: string
  icon: LucideIcon
  visibleFor?: (Client['type'] | Executor['type'])[] // видно всем, если не указано
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
