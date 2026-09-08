'use client'

import React from 'react'
import { Check, Sparkles } from 'lucide-react'

import { Membership } from '@/types/membership'

interface MembershipCardProps {
  plan: Membership
  isCurrent?: boolean
  daysLeft?: number | null
  onSelect?: (planId: number) => void
}

const formatPrice = (price: number) => new Intl.NumberFormat('ru-RU').format(price)

const MembershipCard: React.FC<MembershipCardProps> = ({ plan, isCurrent, daysLeft, onSelect }) => {
  const { id, name, description, price, is_popular, is_available, is_trial, features } = plan

  return (
    <div
      className={`relative flex flex-col rounded-2xl bg-white p-6 shadow transition-shadow hover:shadow-md ${
        is_popular ? 'ring-2 ring-black' : ''
      } ${!is_available ? 'opacity-60' : ''}`}
    >
      {is_popular && (
        <span className="absolute -top-3 left-6 inline-flex items-center gap-1 rounded-full bg-black px-3 py-1 text-xs font-medium text-white">
          <Sparkles className="h-3 w-3" />
          Популярный
        </span>
      )}

      <div className="space-y-1">
        <h3 className="text-lg font-bold text-black">{name}</h3>
        <p className="text-sm text-gray-500">{description}</p>
      </div>

      <div className="mt-4 flex items-baseline gap-1">
        <span className="text-3xl font-bold text-black">{formatPrice(Number(price))} BYN</span>
        <span className="text-sm text-gray-400">/мес</span>
      </div>

      {is_trial && <p className="mt-1 text-xs text-gray-500">Доступен пробный период</p>}

      <ul className="mt-6 flex-1 space-y-3">
        {features.map(feature => (
          <li key={feature.id} className="flex items-start gap-2 text-sm text-black">
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-gray-400" />
            {feature.name}
          </li>
        ))}
      </ul>

      {isCurrent ? (
        <div className="mt-6 rounded-xl bg-gray-100 px-4 py-2 text-center text-sm font-medium text-black">
          {daysLeft != null ? `Ваш тариф · осталось ${daysLeft} дн.` : 'Ваш текущий тариф'}
        </div>
      ) : (
        <button
          type="button"
          disabled={!is_available}
          onClick={() => onSelect?.(id)}
          className="mt-6 rounded-xl bg-black px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
        >
          {is_available ? 'Выбрать тариф' : 'Недоступно'}
        </button>
      )}
    </div>
  )
}

export default MembershipCard
