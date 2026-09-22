import { CarFront, Cog, Package, Truck, type LucideIcon } from 'lucide-react'

export type SearchCategory = {
  id: number
  title: string
  description: string
  href: string
  icon: LucideIcon
}

export type legalNavigation = {
  id: number
  title: string
  href: string
}

export type accountNavigation = {
  id: number
  title: string
  href: string
}

export const searchCategories: SearchCategory[] = [
  {
    id: 1,
    title: 'Перевозчики',
    description: 'Найти транспорт для перевозки',
    href: '/search/carriers',
    icon: Truck,
  },
  {
    id: 2,
    title: 'Поставщики запчастей',
    description: 'Найти необходимые запчасти',
    href: '/search/suppliers',
    icon: Package,
  },
  {
    id: 3,
    title: 'СТО',
    description: 'Найти сервис и ремонт',
    href: '/search/service-stations',
    icon: Cog,
  },
  {
    id: 4,
    title: 'Эвакуаторы',
    description: 'Найти эвакуатор',
    href: '/search/tow-trucks',
    icon: CarFront,
  },
]

export const accountNavigation: accountNavigation[] = [
  {
    id: 1,
    title: 'Войти',
    href: '/login',
  },
  {
    id: 2,
    title: 'Регистрация',
    href: '/register',
  },
]

export const legalNavigation: legalNavigation[] = [
  {
    id: 1,
    title: 'Политика конфиденциальности',
    href: '/privacy-policy',
  },
  {
    id: 2,
    title: 'Пользовательское соглашение',
    href: '/terms-and-conditions',
  },
  // {
  //   id: 3,
  //   title: 'Обработка персональных данных',
  //   href: '/personal-data',
  // },
]
