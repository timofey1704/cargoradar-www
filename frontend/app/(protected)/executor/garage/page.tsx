'use client'

import { TabsContainer } from '@/components/ui/tabs-container'
import { useTabs } from '@/hooks/use-tabs'

import CreateCar from '@/components/account/garage/create-car'
import CarsList from '@/components/account/garage/cars-list'

const TABS = [
  {
    id: 'cars',
    label: 'Мои авто',
    mobileLabel: 'Автомобили',
  },
  {
    id: 'create',
    label: 'Добавить авто',
    mobileLabel: 'Добавить',
  },
] as const

type GarageView = (typeof TABS)[number]['id']

const TAB_IDS = TABS.map(tab => tab.id)

const GaragePage = () => {
  const { selectedTab, setTab, indicatorStyle, tabElements, registerTab } = useTabs<GarageView>(
    TAB_IDS,
    {
      defaultTab: 'cars',
    }
  )
  return (
    <>
      <div className="space-y-8 pb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Список автомобилей</h1>
          <p className="mt-1 text-sm text-gray-500">
            Добавьте или измените данные о Ваших автомобилях.
          </p>
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
        {selectedTab === 'cars' && <CarsList />}
        {selectedTab === 'create' && <CreateCar onCreated={() => setTab('cars')} />}
      </div>
    </>
  )
}

export default GaragePage
