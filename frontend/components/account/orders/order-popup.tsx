'use client'

import { CalendarDays, MapPin, MessageCircle, Package, Truck } from 'lucide-react'
import type { ReactNode } from 'react'

import type { CargoRequest } from '@/types'
import Modal from '@/components/ui/modal'

interface OrderPopupProps {
  order: CargoRequest
  status: {
    label: string
    className: string
  }
  isOpen: boolean
  onClose: () => void
}

const MOCK_CHATS = [
  {
    name: 'Исполнитель 1',
    initials: 'И1',
    message: 'Здравствуйте! Готовы обсудить детали перевозки.',
    time: '10:42',
    unread: true,
  },
  {
    name: 'Исполнитель 2',
    initials: 'И2',
    message: 'Подскажите, груз уже подготовлен к загрузке?',
    time: 'Вчера',
    unread: false,
  },
]

const formatDate = (value: string) => {
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(value))
}

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('ru-RU').format(value)
}

const formatBudget = (value: number | null) => {
  if (value === null) {
    return 'Не указан'
  }

  return `${formatNumber(value)} BYN`
}

export default function OrderPopup({ order, status, isOpen, onClose }: OrderPopupProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Заказ #${order.id}`}>
      <div className="max-h-[calc(100dvh-6rem)] space-y-6 overflow-y-auto p-4 sm:p-6">
        <section>
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-text text-base font-semibold">Информация о заказе</h3>
            <span
              className={[
                'inline-flex rounded-full px-3 py-1 text-xs font-medium',
                status.className,
              ].join(' ')}
            >
              {status.label}
            </span>
          </div>

          <div className="mt-4 rounded-xl bg-gray-50 p-4">
            <div className="flex gap-3">
              <div className="flex flex-col items-center">
                <MapPin size={18} className="text-orange shrink-0" />
                <div className="my-1 h-full min-h-6 w-px bg-gray-300" />
                <MapPin size={18} className="text-orange shrink-0" />
              </div>
              <div className="min-w-0 flex-1 space-y-4">
                <div>
                  <p className="text-xs text-gray-400">Откуда</p>
                  <p className="text-text mt-1 text-sm font-medium">{order.origin_address}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Куда</p>
                  <p className="text-text mt-1 text-sm font-medium">{order.destination_address}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <InfoItem
              icon={<CalendarDays size={18} />}
              label="Дата загрузки"
              value={formatDate(order.loading_date)}
            />
            <InfoItem
              icon={<Package size={18} />}
              label="Груз"
              value={order.cargo_type}
              secondary={[
                `${formatNumber(order.weight_kg)} кг`,
                order.volume_m3 !== null ? `${formatNumber(order.volume_m3)} м³` : null,
              ]
                .filter(Boolean)
                .join(' · ')}
            />
            {order.vehicle_type && (
              <InfoItem icon={<Truck size={18} />} label="Транспорт" value={order.vehicle_type} />
            )}
            <InfoItem
              icon={<CalendarDays size={18} />}
              label="Создан"
              value={formatDate(order.created_at)}
            />
            <div>
              <p className="text-xs text-gray-400">Бюджет</p>
              <p className="text-text mt-1 text-sm font-medium">{formatBudget(order.budget)}</p>
            </div>
          </div>

          {order.comment && (
            <div className="mt-5 border-t border-gray-100 pt-4">
              <p className="text-xs text-gray-400">Комментарий</p>
              <p className="text-text mt-1 text-sm whitespace-pre-wrap">{order.comment}</p>
            </div>
          )}
        </section>

        <section className="border-t border-gray-100 pt-5">
          <div className="flex items-center gap-2">
            <MessageCircle size={18} className="text-orange" />
            <h3 className="text-text text-base font-semibold">Чаты по заказу</h3>
          </div>

          <div className="mt-3 divide-y divide-gray-100">
            {MOCK_CHATS.map(chat => (
              <div key={chat.name} className="flex items-center gap-3 py-3">
                <div className="text-orange flex size-10 shrink-0 items-center justify-center rounded-full bg-orange-50 text-sm font-semibold">
                  {chat.initials}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-text truncate text-sm font-medium">{chat.name}</p>
                    <span className="shrink-0 text-xs text-gray-400">{chat.time}</span>
                  </div>
                  <p className="mt-1 truncate text-sm text-gray-500">{chat.message}</p>
                </div>
                {chat.unread && <span className="bg-orange size-2 shrink-0 rounded-full" />}
              </div>
            ))}
          </div>
        </section>
      </div>
    </Modal>
  )
}

interface InfoItemProps {
  icon: ReactNode
  label: string
  value: string
  secondary?: string
}

function InfoItem({ icon, label, value, secondary }: InfoItemProps) {
  return (
    <div className="flex gap-3">
      <div className="mt-0.5 shrink-0 text-gray-400">{icon}</div>
      <div className="min-w-0">
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-text mt-1 truncate text-sm font-medium">{value}</p>
        {secondary && <p className="mt-1 text-xs text-gray-500">{secondary}</p>}
      </div>
    </div>
  )
}
