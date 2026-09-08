'use client'

import { useQueryClient } from '@tanstack/react-query'

import { useSupportRequests, useCreateSupportRequest } from '@/hooks/use-support-requests'
import { executorRequest } from '@/lib/support/create-request'
import SupportView from '@/components/account/support/support-view'
import showToast from '@/components/ui/toast'

const ExecutorSupportPage = () => {
  const queryClient = useQueryClient()
  const { data: requests = [], isLoading, isError } = useSupportRequests('executor')
  const { mutateAsync: createRequest, isPending } = useCreateSupportRequest(executorRequest)

  const handleSubmit = async (values: Parameters<typeof createRequest>[0]) => {
    await createRequest(values)
    showToast({ type: 'success', message: 'Заявка в поддержку успешно отправлена!' })
    queryClient.invalidateQueries({ queryKey: ['executor-support-requests'] })
  }

  return (
    <SupportView
      requests={requests}
      isLoading={isLoading}
      isError={isError}
      isPending={isPending}
      onSubmit={handleSubmit}
    />
  )
}

export default ExecutorSupportPage
