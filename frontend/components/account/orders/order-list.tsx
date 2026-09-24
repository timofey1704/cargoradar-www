import { LoaderCircle } from 'lucide-react'

import OrderCard from './order-card'

import { useClientOrders } from '@/hooks/use-client-orders'

const OrderList = () => {
  const { data: orders = [], isLoading, isError } = useClientOrders()

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoaderCircle size={28} className="text-orange animate-spin" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-red-100 bg-red-50 px-6 py-10 text-center">
        <h3 className="text-text text-lg font-semibold">Не удалось загрузить заказы</h3>

        <p className="mt-2 text-sm text-gray-500">Попробуйте обновить страницу.</p>
      </div>
    )
  }

  if (orders.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white px-6 py-12 text-center">
        <h3 className="text-text text-lg font-semibold">У вас пока нет заказов</h3>

        <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">
          Создайте первый заказ, чтобы найти исполнителя для перевозки вашего груза.
        </p>
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {orders.map(order => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  )
}

export default OrderList
