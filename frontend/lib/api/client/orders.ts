import { apiRequest } from '@/lib/api'

import type { CargoRequest, CreateCargoRequest } from '@/types'

export const getClientOrders = () => {
  return apiRequest<CargoRequest[]>('/client/orders')
}

export const getClientOrder = (id: number) => {
  return apiRequest<CargoRequest>(`/client/orders/${id}`)
}

export const createClientOrder = (data: CreateCargoRequest) => {
  return apiRequest<CargoRequest>('/client/orders', {
    method: 'POST',
    body: data,
  })
}
