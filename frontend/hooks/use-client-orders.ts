import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { getClientOrders } from '@/lib/api/client/orders'
import { createClientOrder } from '@/lib/api/client/orders'

export const useClientOrders = () => {
  return useQuery({
    queryKey: ['client', 'orders'],
    queryFn: getClientOrders,
  })
}

export const useCreateClientOrder = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createClientOrder,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['client', 'orders'],
      })
    },
  })
}
