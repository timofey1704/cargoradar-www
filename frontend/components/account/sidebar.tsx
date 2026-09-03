'use client'

import React, { useState, useRef, useCallback } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { AccountSidebarProps } from '@/types/client'
import Logout from './logout'
import {
  ClientAccountTypeToDisplayName,
  ExecutorAccountTypeToDisplayName,
  getAccountTypeStyles,
} from '@/consts/accountTypes'
import noPhoto from '../public/images/no-photo.png'
import { TbPhotoUp } from 'react-icons/tb'
import showToast from '../ui/toast'
import { uploadImage } from '@/lib/utils/image-upload'
import { getProxiedImageUrl } from '@/lib/utils/image-proxy'
import Burger from './burger'

type ProfileImageResponse = {
  user: {
    image: string
    [key: string]: string
  }
  message: string
}

const AccountSidebar: React.FC<AccountSidebarProps> = ({ user, navigation }) => {
  const pathname = usePathname()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [previewUrl, setPreviewUrl] = useState<string>(getProxiedImageUrl(user?.image) || '')

  const handlePhotoChange = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    try {
      const file = files[0]

      if (!file.type.startsWith('image/')) {
        showToast({
          type: 'error',
          message: 'Пожалуйста, выберите изображение',
        })
        return
      }

      // создаем превью
      const previewUrl = URL.createObjectURL(file)
      setPreviewUrl(previewUrl)

      // загружаем на сервер
      const response = await uploadImage<ProfileImageResponse>(
        file,
        `${apiUrl}/account/profile/contacts/`
      )

      if (response.user?.image) {
        setPreviewUrl(getProxiedImageUrl(response.user.image))
      }

      showToast({
        type: 'success',
        message: 'Фотография успешно обновлена',
      })

      // очищаем инпут
      e.target.value = ''
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Ошибка при загрузке фотографии',
      })
      console.error('Error handling file:', error)
    }
  }, [])

  if (!user) {
    return null
  }

  const navigationItems = navigation

  return (
    <div className="space-y-3">
      <div className="flex w-full items-center justify-between rounded-2xl bg-white p-2 shadow md:p-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center justify-center">
            <div className="group relative w-full cursor-pointer" onClick={handlePhotoChange}>
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
                height={90}
                width={90}
                priority
                className="aspect-square w-16 rounded-xl object-cover md:w-25 md:rounded-2xl"
              />
              <div className="bg-opacity-40 absolute inset-0 flex items-center justify-center rounded-2xl bg-black opacity-0 transition-opacity group-hover:opacity-100">
                <TbPhotoUp className="text-3xl text-white" />
              </div>
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex gap-2">
              <p className="text-xl font-bold">{user.name || 'Пользователь'}</p>
            </div>

            {/* {user.account_type && (
              <Link
                href="/membership"
                className={`${getAccountTypeStyles(
                  user.account_type
                )} flex items-center justify-center rounded-lg px-3 py-1 text-sm`}
              >
                {
                  accountTypeToDisplayName[
                    user.account_type as keyof typeof accountTypeToDisplayName
                  ]
                }
              </Link>
            )} */}
          </div>
        </div>

        <div className="flex items-center pr-6 sm:pr-10 lg:hidden">
          <Burger navigation={navigation} />
        </div>
      </div>

      <div className="hidden w-full rounded-2xl bg-white p-2 shadow md:w-64 lg:block">
        <nav className="space-y-2">
          {navigationItems.map(item => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`${
                  isActive
                    ? 'border-orange translate-x-2 rounded-l-lg border-r-4 bg-gray-100 text-black'
                    : 'rounded-lg text-gray-600 hover:bg-gray-100'
                } flex items-center p-4 text-sm font-medium transition-all duration-200`}
              >
                <Image
                  src={`/icons/${item.icon}.svg`}
                  alt={item.name}
                  width={20}
                  height={20}
                  className="mr-2"
                />
                {item.name}
              </Link>
            )
          })}
        </nav>
      </div>
      <div className="hidden w-full rounded-2xl bg-white p-2 shadow md:w-64 lg:block">
        <a
          href="https://t.me/+9mMS663WT6Y5YWYy"
          className={`${
            pathname === '/support'
              ? 'border-orange translate-x-2 rounded-l-lg border-r-4 bg-gray-100 text-black'
              : 'rounded-lg text-gray-600 hover:bg-gray-100'
          } flex items-center p-4 text-sm font-medium transition-all duration-200`}
        >
          <Image
            src={`/icons/support.svg`}
            alt={'support'}
            width={20}
            height={20}
            className="mr-2"
          />
          Поддержка
        </a>
        <Logout />
      </div>
    </div>
  )
}

export default AccountSidebar
