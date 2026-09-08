// components/layouts/account-layout-view.tsx
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Toaster } from 'react-hot-toast'

import { Providers } from '@/app/providers/providers'
import AccountSidebar from '@/components/account/sidebar'
import { Loader } from '@/components/ui/loader'
import type { AccountSidebarProps, AccountLayoutViewProps } from '@/types/account'

export default function AccountLayoutView({
  accountType,
  user,
  isAuthChecked,
  loginPath,
  navigation,
  AuthProvider,
  children,
}: AccountLayoutViewProps) {
  const router = useRouter()

  useEffect(() => {
    // редиректим только после того, как AuthProvider закончил проверку авторизации.
    // до этого момента isAuthChecked=false — иначе уезжаем на логин, не дав провайдеру шанса загрузить пользователя
    if (!isAuthChecked) return
    if (!user) router.replace(loginPath)
  }, [isAuthChecked, user, router, loginPath])

  return (
    <Providers>
      <Toaster />
      {/* провайдер обязан монтироваться всегда: именно он дёргает /me,
          заполняет стор и ставит isAuthChecked */}
      <AuthProvider>
        {!isAuthChecked || !user ? (
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
                      {...({
                        accountType,
                        user,
                        navigation: navigation.filter(
                          item => !item.visibleFor || item.visibleFor.includes(user.type)
                        ),
                      } as AccountSidebarProps)}
                    />
                  </div>
                </div>
                <main className="min-w-0 flex-1 px-5">{children}</main>
              </div>
            </div>
          </div>
        )}
      </AuthProvider>
    </Providers>
  )
}
