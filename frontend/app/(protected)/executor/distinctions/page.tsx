import OrderChat from '@/components/account/orders/order-chat'

const DistinctionsPage = () => {
  return (
    <div className="space-y-8 pb-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Чаты</h1>
        <p className="mt-1 text-sm text-gray-500">Переписки с заказчиками по вашим предложениям.</p>
      </div>

      <OrderChat isOpen currentRole="executor" />
    </div>
  )
}

export default DistinctionsPage
