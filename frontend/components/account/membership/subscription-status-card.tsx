import type { SubscriptionRead } from '@/types/index'

const STATUS_LABELS: Record<string, string> = {
  active: 'Активна',
  expired: 'Истекла',
  cancelled: 'Отменена',
}

interface SubscriptionStatusCardProps {
  subscription: SubscriptionRead
  daysLeft: number | null
}

const formatDate = (value: string) =>
  new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).format(
    new Date(value)
  )

const SubscriptionStatusCard: React.FC<SubscriptionStatusCardProps> = ({
  subscription,
  daysLeft,
}) => {
  const { status, subscription_end, auto_renewal, membership } = subscription

  return (
    <div className="flex flex-col justify-between gap-4 rounded-2xl bg-white p-6 shadow sm:flex-row sm:items-center">
      <div>
        <div className="flex items-center gap-2">
          <p className="text-base font-bold text-black">{membership.name}</p>
          <span className="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
            {STATUS_LABELS[status] ?? status}
          </span>
        </div>

        <p className="mt-1 text-sm text-gray-500">
          {auto_renewal
            ? `Автопродление ${formatDate(subscription_end)}`
            : `Действует до ${formatDate(subscription_end)}`}
        </p>
      </div>

      {daysLeft != null && (
        <div className="text-sm text-gray-500">
          осталось <span className="font-semibold text-black">{daysLeft} дн.</span>
        </div>
      )}
    </div>
  )
}

export default SubscriptionStatusCard
