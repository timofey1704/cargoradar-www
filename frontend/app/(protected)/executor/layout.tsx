'use client'

import { User, Package, MessageSquareReply, Headset, Banknote, CarFront } from 'lucide-react'

import useExecutorStore from '@/store/executorStore'
import ExecutorAuthProvider from '@/app/providers/executor-auth-provider'
import AccountLayoutView from '@/components/layouts/account-layout-view'
import type { NavigationItem } from '@/types'

const executorNavigation: NavigationItem[] = [
  { name: 'Профиль', href: '/executor', icon: User },
  { name: 'Заказы', href: '/executor/orders', icon: Package },
  { name: 'Гараж', href: '/executor/garage', icon: CarFront, visibleFor: ['carrier'] },
  { name: 'Отклики', href: '/executor/distinctions', icon: MessageSquareReply },
  { name: 'Поддержка', href: '/executor/support', icon: Headset },
  { name: 'Подписка', href: '/executor/membership', icon: Banknote },
]

export default function ExecutorLayout({ children }: { children: React.ReactNode }) {
  const { executor, isAuthChecked } = useExecutorStore()

  return (
    <AccountLayoutView
      accountType="executor"
      user={executor}
      isAuthChecked={isAuthChecked}
      loginPath="/login/executor"
      navigation={executorNavigation}
      AuthProvider={ExecutorAuthProvider}
    >
      {children}
    </AccountLayoutView>
  )
}
