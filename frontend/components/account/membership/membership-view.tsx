'use client'

import MembershipCard from '@/components/account/membership/membership-card'
import SubscriptionStatusCard from '@/components/account/membership/subscription-status-card'
import type { MembershipInfo } from '@/types/membership'

interface MembershipViewProps {
  membershipInfo: MembershipInfo | undefined
  isLoading: boolean
  isError: boolean
}

const MembershipView = ({ membershipInfo, isLoading, isError }: MembershipViewProps) => {
  return (
    <div className="space-y-8 pb-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Подписка</h1>
        <p className="mt-1 text-sm text-gray-500">
          Информация о вашей подписке и доступных тарифах.
        </p>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-80 animate-pulse rounded-2xl bg-gray-100" />
          ))}
        </div>
      )}

      {isError && (
        <div className="rounded-2xl bg-white p-6 text-sm text-gray-500 shadow">
          Не удалось загрузить данные о подписке. Попробуйте обновить страницу.
        </div>
      )}

      {membershipInfo && (
        <>
          {membershipInfo.subscription && (
            <SubscriptionStatusCard
              subscription={membershipInfo.subscription}
              daysLeft={membershipInfo.days_left}
            />
          )}

          <div>
            <h2 className="text-2xl! font-semibold text-gray-900">Доступные тарифы</h2>

            <div className="mt-4 grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {membershipInfo.plans.map(plan => (
                <MembershipCard
                  key={plan.id}
                  plan={plan}
                  isCurrent={membershipInfo.subscription?.membership.id === plan.id}
                  daysLeft={membershipInfo.days_left}
                  onSelect={planId => {
                    // TODO: подключить bepaid
                    console.log('select plan', planId)
                  }}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default MembershipView
