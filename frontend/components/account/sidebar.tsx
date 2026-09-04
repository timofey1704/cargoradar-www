'use client'

import React, { useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import Logout from './logout'
import { getAccountTypeConfig } from '@/consts/accountTypes'
import noPhoto from '../../public/images/no-photo.png'
import { TbPhotoUp } from 'react-icons/tb'
import showToast from '../ui/toast'
import { uploadImage } from '@/lib/utils/image-upload'
import { getProxiedImageUrl } from '@/lib/utils/image-proxy'
import Burger from './burger'
import type { AccountSidebarProps } from './types'
import { navItemClassName } from './navItemStyles'

type ProfileImageResponse = {
  user: { image: string; [key: string]: string }
  message: string
}

const AccountSidebar: React.FC<AccountSidebarProps> = ({ accountType, user, navigation }) => {
  const pathname = usePathname()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [previewUrl, setPreviewUrl] = useState<string>(getProxiedImageUrl(user?.image) || '')

  const handlePhotoChange = () => fileInputRef.current?.click()

  const handleFileChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (!files || files.length === 0) return
      const apiUrl = process.env.NEXT_PUBLIC_API_URL

      try {
        const file = files[0]
        if (!file.type.startsWith('image/')) {
          showToast({ type: 'error', message: 'Пожалуйста, выберите изображение' })
          return
        }

        const preview = URL.createObjectURL(file)
        setPreviewUrl(preview)

        // эндпоинт для фоток
        const endpoint =
          accountType === 'client'
            ? `${apiUrl}/account/profile/contacts/`
            : `${apiUrl}/executor/profile/contacts/`

        const response = await uploadImage<ProfileImageResponse>(file, endpoint)

        if (response.user?.image) {
          setPreviewUrl(getProxiedImageUrl(response.user.image))
        }

        showToast({ type: 'success', message: 'Фотография успешно обновлена' })
        e.target.value = ''
      } catch (error) {
        showToast({ type: 'error', message: 'Ошибка при загрузке фотографии' })
        console.error('Error handling file:', error)
      }
    },
    [accountType]
  )

  if (!user) return null

  const { label: accountTypeLabel, className: accountTypeClassName } =
    accountType === 'client'
      ? getAccountTypeConfig('client', user.type)
      : getAccountTypeConfig('executor', user.type)

  return (
    <div className="space-y-3">
      <div className="flex w-full items-center justify-between rounded-2xl bg-white p-2 shadow md:p-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center">
            <div className="group relative cursor-pointer" onClick={handlePhotoChange}>
              <input
                type="file"
                id="image"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept="image/*"
              />
              <Image
                src={previewUrl || getProxiedImageUrl(user.image) || noPhoto}
                alt="profile image"
                height={45}
                width={45}
                priority
                className="aspect-square w-12 rounded-lg object-cover md:w-16 md:rounded-xl"
              />
              <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-black/40 opacity-0 transition-opacity group-hover:opacity-100 md:rounded-xl">
                <TbPhotoUp className="text-sm text-white md:text-base" />
              </div>
            </div>
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
