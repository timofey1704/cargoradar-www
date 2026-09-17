'use client'

import React, { useState, useRef, useEffect } from 'react'
import { AccordionProps } from '@/types'
import closedFAQ from '../../public/icons/closedFAQ.svg'
import openFAQ from '../../public/icons/openFAQ.svg'
import Image from 'next/image'

const Accordion: React.FC<AccordionProps> = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)
  const [contentHeight, setContentHeight] = useState<number>(0)

  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight)
    }
  }, [content])

  const renderContent = () => {
    if (typeof content === 'string') {
      return (
        <div
          className="lg:text-md [&_a]:text-gradient text-sm font-medium sm:text-base [&_a]:hover:underline [&_li]:mb-1 sm:[&_li]:mb-2 [&_p]:mt-1 [&_ul]:list-disc [&_ul]:py-1.5 [&_ul]:pl-3 sm:[&_ul]:py-2 sm:[&_ul]:pl-4 [&>ol]:list-decimal [&>ol]:pl-3 sm:[&>ol]:pl-4"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      )
    }
    return <p className="lg:text-md text-sm font-medium text-black sm:text-base">{content}</p>
  }

  return (
    <div className="bg-text relative my-3 border-y-2 border-[#F1F1F1] sm:my-4">
      <button
        className="flex w-full items-center justify-between py-5 sm:py-4 lg:py-8"
        onClick={() => setIsOpen(!isOpen)}
      >
        <h5 className="text-left text-sm text-black sm:text-base lg:text-lg">{title}</h5>
        <div className="relative flex h-6 w-6 shrink-0 items-center justify-center sm:h-7 sm:w-7 lg:h-8 lg:w-8">
          <Image
            src={openFAQ}
            alt="FAQ icon"
            width={32}
            height={32}
            className={`absolute h-full w-full transition-all duration-500 ${
              isOpen ? 'rotate-0 opacity-100' : '-rotate-180 opacity-0'
            }`}
          />
          <Image
            src={closedFAQ}
            alt="FAQ icon"
            width={32}
            height={32}
            className={`absolute h-full w-full transition-all duration-500 ${
              isOpen ? 'rotate-180 opacity-0' : 'rotate-0 opacity-100'
            }`}
          />
        </div>
      </button>

      <div
        ref={contentRef}
        style={{ '--accordion-height': `${contentHeight}px` } as React.CSSProperties}
        className={`grid transition-all duration-500 ease-in-out ${
          isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        } `}
      >
        <div className="overflow-hidden">
          <div className="pr-4 pb-3 sm:pr-6 sm:pb-4 lg:pr-8 lg:pb-5">
            <div className="text-black">{renderContent()}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Accordion
