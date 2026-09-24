import { ArrowRight, CalendarDays, MapPin, Package, Truck } from 'lucide-react'
import Link from 'next/link'

import type { ReactNode } from 'react'

import type { CargoRequest } from '@/types'

interface OrderCardProps {
  order: CargoRequest
}

const STATUS_CONFIG: Record<
  CargoRequest['status'],
  {
    label: string
    className: string
  }
> = {
  new: {
    label: 'Новый',
    className: 'bg-blue-50 text-blue-700',
  },
  in_progress: {
    label: 'В работе',
    className: 'bg-orange-50 text-orange-700',
  },
  completed: {
    label: 'Завершён',
    className: 'bg-green-50 text-green-700',
  },
  cancelled: {
    label: 'Отменён',
    className: 'bg-red-50 text-red-700',
  },
}

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

export default function OrderCard({ order }: OrderCardProps) {
  const status = STATUS_CONFIG[order.status]

  return (
    <article className="rounded-2xl border border-gray-200 bg-white p-5">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-gray-400">Заказ #{order.id}</p>

          <span
            className={[
              'mt-2 inline-flex rounded-full px-3 py-1',
              'text-xs font-medium',
              status.className,
            ].join(' ')}
          >
            {status.label}
          </span>
        </div>

        <p className="text-sm text-gray-400">{formatDate(order.created_at)}</p>
      </div>

      {/* Route */}
      <div className="mt-5 rounded-xl bg-gray-50 p-4">
        <div className="flex gap-3">
          <div className="flex flex-col items-center">
            <MapPin size={18} className="text-orange shrink-0" />

            <div className="my-1 h-full min-h-6 w-px bg-gray-300" />

            <MapPin size={18} className="text-orange shrink-0" />
          </div>

          <div className="min-w-0 flex-1">
            <div>
              <p className="text-xs text-gray-400">Откуда</p>

              <p className="text-text mt-1 text-sm font-medium">{order.origin_address}</p>
            </div>

            <div className="mt-4">
              <p className="text-xs text-gray-400">Куда</p>

              <p className="text-text mt-1 text-sm font-medium">{order.destination_address}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Information */}
      <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
      </div>

      {/* Footer */}
      <div className="mt-5 flex items-end justify-between gap-4 border-t border-gray-100 pt-4">
        <div>
          <p className="text-xs text-gray-400">Бюджет</p>

          <p className="text-text mt-1 text-lg font-semibold">{formatBudget(order.budget)}</p>
        </div>

        <Link
          href={`/account/orders/${order.id}`}
          className="text-orange inline-flex items-center gap-1 text-sm font-medium transition-colors hover:text-[#e65322]"
        >
          Подробнее
          <ArrowRight size={16} />
        </Link>
      </div>

      {/* Comment */}
      {order.comment && (
        <div className="mt-4 border-t border-gray-100 pt-4">
          <p className="line-clamp-2 text-sm text-gray-500">{order.comment}</p>
        </div>
      )}
    </article>
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
