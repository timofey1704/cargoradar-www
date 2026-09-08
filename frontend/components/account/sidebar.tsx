'use client'

import React from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import Logout from './logout'
import { getAccountTypeConfig } from '@/consts/accountTypes'
import { getProxiedImageUrl } from '@/lib/utils/image-proxy'
import Burger from './burger'
import type { AccountSidebarProps } from '@/types'
import { navItemClassName } from './navItemStyles'

const AccountSidebar: React.FC<AccountSidebarProps> = ({ accountType, user, navigation }) => {
  const pathname = usePathname()

  if (!user) return null

  const { label: accountTypeLabel, className: accountTypeClassName } =
    accountType === 'client'
      ? getAccountTypeConfig('client', user.type)
      : getAccountTypeConfig('executor', user.type)

  // стили бейджа подписки: premium — золотой, free — нейтральный синий,
  // без подписки — приглушённый серый
  const memberValue = user.membership?.toLowerCase()
  const isPremium = memberValue === 'premium'

  const membershipClassName = isPremium
    ? 'bg-amber-100 text-amber-700'
    : user.membership
      ? 'bg-sky-100 text-sky-700'
      : 'bg-gray-100 text-gray-500'

  return (
    <div className="space-y-3">
      <div className="flex w-full items-center justify-between rounded-2xl bg-white p-2 shadow md:p-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center">
            <Image
              src={getProxiedImageUrl(user.image)}
              alt="profile image"
              height={90}
              width={90}
              priority
              className="aspect-square w-16 rounded-xl object-cover md:w-25 md:rounded-2xl"
            />
          </div>
          <div className="space-y-1">
            <div className="flex gap-2">
              <p className="text-sm font-bold text-black md:text-base">
                {user.name || 'Пользователь'}
              </p>
            </div>

            <span
              className={`${accountTypeClassName} inline-flex items-center justify-center rounded-md px-2 py-0.5 text-xs`}
            >
              {accountTypeLabel}
            </span>
            <span
              className={`inline-flex items-center justify-center rounded-md px-2 py-0.5 text-xs ${membershipClassName}`}
            >
              {user.membership || 'Нет подписки'}
            </span>
          </div>
        </div>

        <div className="flex items-center pr-6 sm:pr-10 lg:hidden">
          <Burger navigation={navigation} accountType={accountType} />
        </div>
      </div>

      <div className="hidden w-full rounded-2xl bg-white p-2 shadow md:w-64 lg:block">
        <nav className="space-y-2">
          {navigation.map(item => {
            const isActive = pathname === item.href
            const Icon = item.icon
            return (
              <Link key={item.name} href={item.href} className={navItemClassName(isActive)}>
                <Icon className="mr-2 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
          <Logout accountType={accountType} />
        </nav>
      </div>
    </div>
  )
}

export default AccountSidebar
