'use client'

import { Providers } from '@/app/providers/providers'
import ExecutorAuthProvider from '../../providers/executor-auth-provider'
import { Toaster } from 'react-hot-toast'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { User, Package, MessageSquareReply, Headset, Banknote, CarFront } from 'lucide-react'
import useExecutorStore from '@/store/executorStore'
import AccountSidebar from '@/components/account/sidebar'
import { Loader } from '@/components/ui/loader'
import { Executor } from '@/types'
import { NavigationItem } from '@/types'

export default function ExecutorLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { executor, isAuthChecked } = useExecutorStore()

  useEffect(() => {
    // редиректим только после того, как executorAuthProvider закончил проверку авторизации.
    // жо этого момента isAuthChecked=false — иначе уезжаем на логин, не дав провайдеру шанса загрузить клиента

    if (!isAuthChecked) return

    if (!executor) {
      router.replace('/login/executor')
    }
  }, [isAuthChecked, executor, router])

  const executorNavigation: NavigationItem[] = [
    { name: 'Профиль', href: '/executor', icon: User },
    {
      name: 'Заказы',
      href: '/executor/orders',
      icon: Package,
    },
    { name: 'Гараж', href: '/executor/garage', icon: CarFront, visibleFor: ['carrier'] },
    { name: 'Отклики', href: '/executor/distinctions', icon: MessageSquareReply },
    { name: 'Поддержка', href: '/executor/support', icon: Headset },
    { name: 'Подписка', href: '/executor/membership', icon: Banknote },
  ]

  function getExecutorNavigation(user: Executor) {
    return executorNavigation.filter(
      item => !item.visibleFor || item.visibleFor.includes(user.type)
    )
  }

  return (
    <Providers>
      <Toaster />
      {/* провайдер обязан монтироваться всегда: именно он дёргает /me,
          заполняет стор и ставит isAuthChecked */}
      <ExecutorAuthProvider>
        {!isAuthChecked || !executor ? (
          <div className="flex min-h-screen items-center justify-center bg-[#F3F3F3]">
            <Loader />
          </div>
        ) : (
          <div className="min-h-screen bg-[#F3F3F3]">
            <div className="mx-auto max-w-337.5 px-4 pt-8 sm:px-6">
              <div className="flex flex-col gap-6 md:flex-row">
                <div className="w-full shrink-0 md:w-64">
                  <div className="sticky top-8">
                    <AccountSidebar
                      accountType="executor"
                      user={executor}
                      navigation={getExecutorNavigation(executor)}
                    />
                  </div>
                </div>
                <main className="min-w-0 flex-1 px-5">{children}</main>
              </div>
            </div>
          </div>
        )}
      </ExecutorAuthProvider>
    </Providers>
  )
}
