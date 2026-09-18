'use client'

import React, { useRef, useEffect } from 'react'

interface ScrollProps {
  moveTo: string
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

const Scroll = ({ moveTo, children, onClick, className }: ScrollProps) => {
  const ref = useRef<HTMLElement | null>(null)

  useEffect(() => {
    ref.current = document.querySelector<HTMLElement>(`#${moveTo}`)
  }, [moveTo])

  const handleClick = () => {
    const element = ref.current
    if (element) {
      const elementPosition = element.getBoundingClientRect().top
      const offsetPosition = elementPosition + window.scrollY - 15

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      })
    }

    // для мобилки
    if (onClick) onClick()
  }

  return (
    <div onClick={handleClick} className={`${className}`}>
      {children}
    </div>
  )
}

export default Scroll
