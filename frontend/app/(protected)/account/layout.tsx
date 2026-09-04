'use client'

import { Toaster } from 'react-hot-toast'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Providers } from '@/app/providers/providers'
import ClientAuthProvider from '../../providers/client-auth-provider'
import useClientStore from '@/store/clientStore'
import AccountSidebar from '@/components/account/sidebar'
import { Loader } from '@/components/ui/loader'
import { Client } from '@/types'

type NavItem = {
  name: string
  href: string
  icon: string
  visibleFor?: Client['type'][] // если не указано — видно всем
}

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { client, isAuthChecked } = useClientStore()

  useEffect(() => {
    // редиректим только после того, как ClientAuthProvider закончил проверку авторизации.
    // жо этого момента isAuthChecked=false — иначе уезжаем на логин, не дав провайдеру шанса загрузить клиента

    if (!isAuthChecked) return

    if (!client) {
      router.replace('/login/client')
    }
  }, [isAuthChecked, client, router])

  const clientNavigation: NavItem[] = [
    { name: 'Профиль', href: '/account', icon: 'profile' },
    { name: 'Заказы', href: '/account/orders', icon: 'orders' },
    { name: 'Отклики', href: '/account/distinctions', icon: 'distinctions' },
    { name: 'Поддержка', href: '/account/support', icon: 'support' },
    { name: 'Подписка', href: '/account/membership', icon: 'membership', visibleFor: ['legal'] },
  ]

  function getClientNavigation(user: Client) {
    return clientNavigation.filter(item => !item.visibleFor || item.visibleFor.includes(user.type))
  }

  return (
    <Providers>
      <Toaster />
      {/* провайдер обязан монтироваться всегда: именно он дёргает /me,
          заполняет стор и ставит isAuthChecked */}
      <ClientAuthProvider>
        {!isAuthChecked || !client ? (
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
                      accountType="client"
                      user={client}
                      navigation={getClientNavigation(client)}
                    />
                  </div>
                </div>
                <main className="min-w-0 flex-1 px-5">{children}</main>
              </div>
            </div>
          </div>
        )}
      </ClientAuthProvider>
    </Providers>
  )
}
