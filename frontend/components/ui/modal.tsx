'use client'

import React, { useEffect } from 'react'
import { createPortal } from 'react-dom'
import { IoClose } from 'react-icons/io5'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth
      document.body.style.paddingRight = `${scrollbarWidth}px`
      document.body.style.overflow = 'hidden'

      // добавляем контроль z-index для карт
      const mapContainers = document.querySelectorAll(
        '.map-container, [class*="ymaps"], [class*="gm-"]'
      )
      mapContainers.forEach(container => {
        if (container instanceof HTMLElement) {
          container.style.zIndex = '10'
        }
      })
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.paddingRight = '0px'
      document.body.style.overflow = 'unset'

      // возвращаем z-index карт чтобы попап не налазил на карту
      const mapContainers = document.querySelectorAll(
        '.map-container, [class*="ymaps"], [class*="gm-"]'
      )
      mapContainers.forEach(container => {
        if (container instanceof HTMLElement) {
          container.style.zIndex = ''
        }
      })
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 z-9999 overflow-y-auto">
      <div
        className="fixed inset-0 bg-black transition-opacity duration-300 ease-in-out"
        style={{
          opacity: isOpen ? 0.5 : 0,
        }}
        onClick={onClose}
      />

      <div className="bg-opacity-70 z-10000 flex min-h-full items-center justify-center backdrop-blur-sm">
        <div
          className={`relative min-h-screen w-full transform overflow-hidden bg-white text-left shadow-xl transition-all duration-300 ease-in-out sm:m-4 sm:min-h-0 sm:max-w-3xl sm:rounded-2xl ${isOpen ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'} animate-[modalShow_0.3s_ease-out]`}
        >
          <div className="flex items-center justify-between border-b border-gray-100 p-4 sm:p-6">
            <h2 className="text-xl font-bold sm:text-2xl">{title}</h2>
            <button
              onClick={onClose}
              className="rounded-xl bg-gray-500 p-2 text-white transition-colors duration-200 ease-in-out hover:bg-gray-400 hover:text-black"
            >
              <IoClose size={24} />
            </button>
          </div>

          {children}
        </div>
      </div>
    </div>,
    document.body
  )
}

export default Modal
