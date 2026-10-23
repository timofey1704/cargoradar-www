import OrderChat from '@/components/account/orders/order-chat'

const DistinctionsPage = () => {
  return (
    <div className="space-y-8 pb-8">
      <OrderChat isOpen currentRole="executor" />
    </div>
  )
}

export default DistinctionsPage
