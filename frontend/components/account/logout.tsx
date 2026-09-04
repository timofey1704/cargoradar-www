'use client'

import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { useState } from 'react'
import clsx from 'clsx'
import { navItemClassName } from './navItemStyles'
import useClientStore from '@/store/clientStore'
import useExecutorStore from '@/store/executorStore'
import showToast from '../ui/toast'

const LOGOUT_ENDPOINTS = {
  client: '/client/auth/logout',
  executor: '/executor/auth/logout',
} as const

interface LogoutProps {
  accountType: 'client' | 'executor'
  onClick?: () => void
}

const Logout: React.FC<LogoutProps> = ({ accountType, onClick }) => {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const apiUrl = process.env.NEXT_PUBLIC_API_URL

  const handleLogout = async () => {
    if (isLoading) return

    setIsLoading(true)

    try {
      const response = await fetch(`${apiUrl}${LOGOUT_ENDPOINTS[accountType]}`, {
        method: 'POST',
        credentials: 'include',
      })

      if (!response.ok) {
        throw new Error('Logout failed')
      }

      if (accountType === 'client') {
        useClientStore.getState().logout()
      } else {
        useExecutorStore.getState().logout()
      }

      // закрываем бургер
      onClick?.()

      // редирект
      showToast({ type: 'success', message: 'Успешно вышли из аккаунта!' })
      router.replace(`/login/${accountType}`)
    } catch (error) {
      console.error('Logout error:', error)
      showToast({ type: 'error', message: 'Не удалось выйти из аккаунта' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <button
      onClick={handleLogout}
      className={clsx(
        navItemClassName(false),
        'hover:border-orange rounded-2xl bg-white text-gray-600 hover:cursor-pointer',
        isLoading && 'cursor-not-allowed opacity-50',
        !isLoading && 'hover:bg-gray-50'
      )}
      disabled={isLoading}
    >
      <Image src="/icons/logout.png" alt="Выйти" width={20} height={20} className="mr-2" />
      {isLoading ? 'Выход...' : 'Выйти'}
    </button>
  )
}

export default Logout
