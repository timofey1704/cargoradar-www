'use client'

import { TabsContainer } from '@/components/ui/tabs-container'
import { useTabs } from '@/hooks/use-tabs'

import OrdersList from '@/components/account/orders/order-list'
import CreateOrder from '@/components/account/orders/create-order'

const TABS = [
  {
    id: 'orders',
    label: 'Мои заказы',
    mobileLabel: 'Заказы',
  },
  {
    id: 'create',
    label: 'Создать заказ',
    mobileLabel: 'Создать',
  },
] as const

type OrderView = (typeof TABS)[number]['id']

const TAB_IDS = TABS.map(tab => tab.id)

export default function OrdersPage() {
  const { selectedTab, setTab, indicatorStyle, tabElements, registerTab } = useTabs<OrderView>(
    TAB_IDS,
    {
      defaultTab: 'orders',
    }
  )

  return (
    <div>
      <div className="space-y-8 pb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Заказы</h1>

          <p className="mt-1 text-sm text-gray-500">Добавляйте и работайте с Вашими заказами.</p>
        </div>
      </div>

      <TabsContainer
        tabs={TABS}
        selectedTab={selectedTab}
        indicatorStyle={indicatorStyle}
        tabElements={tabElements}
        registerTab={registerTab}
        onTabChange={setTab}
      />

      <div className="my-6">
        {selectedTab === 'orders' && <OrdersList />}
        {selectedTab === 'create' && <CreateOrder onCreated={() => setTab('orders')} />}
      </div>
    </div>
  )
}
