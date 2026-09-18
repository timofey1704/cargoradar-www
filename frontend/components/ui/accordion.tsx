'use client'

import React, { useId, useState } from 'react'
import { Plus } from 'lucide-react'
import { AccordionProps } from '@/types'

const Accordion: React.FC<AccordionProps> = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(false)
  const contentId = useId()

  const renderContent = () => {
    if (typeof content === 'string') {
      return (
        <div
          className="[&_a]:text-orange [&_strong]:text-text text-sm leading-6 font-medium text-gray-600 sm:text-base sm:leading-7 [&_a]:font-semibold [&_a]:hover:underline [&_li]:mb-1 sm:[&_li]:mb-2 [&_p]:mt-2 [&_p:first-child]:mt-0 [&_ul]:list-disc [&_ul]:py-1.5 [&_ul]:pl-5 sm:[&_ul]:py-2 [&>ol]:list-decimal [&>ol]:pl-5"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      )
    }

    return (
      <p className="text-sm leading-6 font-medium text-gray-600 sm:text-base sm:leading-7">
        {content}
      </p>
    )
  }

  return (
    <div
      className={`overflow-hidden rounded-2xl border bg-white transition-all duration-300 ${
        isOpen
          ? 'border-orange/30 shadow-orange/5 shadow-lg'
          : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
      }`}
    >
      <button
        type="button"
        aria-expanded={isOpen}
        aria-controls={contentId}
        onClick={() => setIsOpen(prev => !prev)}
        className="focus-visible:ring-orange/40 flex w-full cursor-pointer items-center justify-between gap-6 px-5 py-5 text-left focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-white focus-visible:outline-none sm:px-6 sm:py-6"
      >
        <h5
          className={`text-base font-semibold transition-colors sm:text-lg ${
            isOpen ? 'text-orange' : 'text-text'
          }`}
        >
          {title}
        </h5>

        <span
          aria-hidden="true"
          className={`flex size-9 shrink-0 items-center justify-center rounded-full transition-colors duration-300 sm:size-10 ${
            isOpen ? 'bg-orange text-white' : 'bg-orange/10 text-orange'
          }`}
        >
          <Plus
            className={`size-5 transition-transform duration-300 ${isOpen ? 'rotate-45' : 'rotate-0'}`}
          />
        </span>
      </button>

      <div
        id={contentId}
        className={`grid transition-[grid-template-rows,opacity] duration-300 ease-in-out ${
          isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <div className="border-t border-gray-100 px-5 py-5 sm:px-6 sm:py-6">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Accordion
