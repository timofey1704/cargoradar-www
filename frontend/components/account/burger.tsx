'use client'

import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import type { BurgerProps } from './types'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import Logout from './logout'

const Burger: React.FC<BurgerProps> = ({ navigation, accountType }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

  const handleClose = () => setIsOpen(false)

  const pathname = usePathname()
  const navigationItems = navigation

  useEffect(() => {
    setMounted(true)
  }, [])

  const menuContent = (
    <div
      className={`fixed left-0 z-99998 w-full origin-top bg-[#F3F3F3] transition-all duration-300 ease-in-out ${
        isOpen
          ? 'top-30 h-[calc(100vh-80px)] scale-y-100 opacity-100'
          : 'top-20 h-0 scale-y-0 opacity-0'
      } ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`}
    >
      <div
        className={`flex flex-col items-center space-y-3 px-4 pt-4 transition-all duration-300 ${
          isOpen ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
        }`}
      >
        <div className="w-full rounded-2xl bg-white p-2 shadow md:w-64">
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
                  onClick={handleClose}
                >
                  <Image
                    src={`/icons/${item.icon}.png`}
                    alt={item.name}
                    width={20}
                    height={20}
                    className="mr-2"
                  />
                  {item.name}
                </Link>
              )
            })}
            <Logout accountType={accountType} onClick={handleClose} />
          </nav>
        </div>
      </div>
    </div>
  )

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative z-99999 flex h-8 w-8 flex-col items-center justify-center"
      >
        <div className="relative h-8 w-8">
          <span
            className={`absolute h-0.5 bg-black transition-all duration-300 ease-in-out ${
              isOpen ? 'top-4 w-8 rotate-45' : 'top-2 w-8'
            }`}
          />
          <span
            className={`absolute h-0.5 bg-black transition-all duration-300 ease-in-out ${
              isOpen ? 'top-4 w-0 opacity-0' : 'top-4 w-8'
            }`}
          />
          <span
            className={`absolute h-0.5 bg-black transition-all duration-300 ease-in-out ${
              isOpen ? 'top-4 w-8 -rotate-45' : 'top-6 w-8'
            }`}
          />
        </div>
      </button>

      {mounted && createPortal(menuContent, document.body)}
    </>
  )
}

export default Burger
