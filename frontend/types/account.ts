import type { LucideIcon } from 'lucide-react'
import type { Client } from '@/types/client'
import type { Executor } from '@/types/executor'

export interface AccountLayoutViewProps {
  accountType: 'client' | 'executor'
  user: Client | Executor | null
  isAuthChecked: boolean
  loginPath: string
  navigation: NavigationItem[]
  AuthProvider: React.ComponentType<{ children: React.ReactNode }>
  children: React.ReactNode
}

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

export interface SupportTicket {
  id: number
  title: string
  description: string
  request_type: string
  status: string
  created_at: string
  updated_at: string
}
