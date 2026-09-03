export interface Client {
  id: number
  name: string
  email: string
  phone_number: string
  image?: string
  VIN_code: string | null
  is_notifications_enabled: boolean
  is_active: boolean
}

export interface NavigationItem {
  name: string
  href: string
  icon: string
}

export interface AccountSidebarProps {
  user: Client
  navigation: NavigationItem[]
}

export type BurgerProps = Pick<AccountSidebarProps, 'navigation'>
