'use client'

import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import type { BurgerProps } from '@/types'
import Link from 'next/link'
import { navItemClassName } from './navItemStyles'
import { usePathname } from 'next/navigation'
import Logout from './logout'

const Burger: React.FC<BurgerProps> = ({ navigation, accountType }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

  const pathname = usePathname()

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
