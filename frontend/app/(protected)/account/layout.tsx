'use client'

import { User, Package, MessageSquareReply, Headset, Banknote, CarFront } from 'lucide-react'

import useClientStore from '@/store/clientStore'
import ClientAuthProvider from '@/app/providers/client-auth-provider'
import AccountLayoutView from '@/components/layouts/account-layout-view'
import type { NavigationItem } from '@/types'

const clientNavigation: NavigationItem[] = [
  { name: 'Профиль', href: '/account', icon: User },
  { name: 'Заказы', href: '/account/orders', icon: Package },
  { name: 'Отклики', href: '/account/distinctions', icon: MessageSquareReply },
  { name: 'Поддержка', href: '/account/support', icon: Headset },
  { name: 'Подписка', href: '/account/membership', icon: Banknote, visibleFor: ['legal'] },
]

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  const { client, isAuthChecked } = useClientStore()

  return (
    <AccountLayoutView
      accountType="client"
      user={client}
      isAuthChecked={isAuthChecked}
      loginPath="/login/client"
      navigation={clientNavigation}
      AuthProvider={ClientAuthProvider}
    >
      {children}
    </AccountLayoutView>
  )
}
