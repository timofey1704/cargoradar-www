import type { AccordionProps } from './accordion'

/** Элемент FAQ для главной страницы (соответствует FAQRead на бэкенде). */
export type Faq = AccordionProps & {
  id: number
  content: string
}