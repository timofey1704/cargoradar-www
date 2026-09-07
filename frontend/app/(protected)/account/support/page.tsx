'use client'

import { FormProvider } from 'react-hook-form'
import { Ticket } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'

import { useAppForm } from '@/hooks/use-app-form'
import { FormInput } from '@/components/ui/form-input'
import { FormSelect } from '@/components/ui/form-select'
import { Button } from '@/components/ui/button'
import { supportSchema, type SupportFormInput } from '@/schemas/support/createRequest'
import { useCreateSupportRequest } from '@/hooks/use-support-requests'
import { useSupportRequests } from '@/hooks/use-support-requests'
import { clientRequest } from '@/lib/support/create-request'
import showToast from '@/components/ui/toast'

const requestTypeOptions = [
  {
    value: 'solution',
    label: 'Предложение',
  },
  {
    value: 'error',
    label: 'Ошибка',
  },
]

const requestTypeLabels: Record<string, string> = {
  solution: 'Предложение',
  error: 'Ошибка',
}

const statusConfig: Record<string, { label: string; className: string }> = {
  new: { label: 'Новое', className: 'bg-blue-50 text-blue-600' },
  in_progress: { label: 'В работе', className: 'bg-orange-50 text-orange-600' },
  needs_info: { label: 'Нужна информация', className: 'bg-yellow-50 text-yellow-600' },
  resolved: { label: 'Решено', className: 'bg-green-50 text-green-600' },
  rejected: { label: 'Отклонено', className: 'bg-red-50 text-red-600' },
}

function formatDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('ru-RU')
}

const SupportPage = () => {
  const { form, handleSubmit } = useAppForm({
    schema: supportSchema,
    defaultValues: {
      requestType: '',
      title: '',
      description: '',
    },
    onClean: true,
  })

  const queryClient = useQueryClient()
  const { data: requests = [], isLoading, isError } = useSupportRequests()
  const { mutateAsync: createRequest, isPending } = useCreateSupportRequest(clientRequest)

  const handleCreateSupportRequest = handleSubmit(async values => {
    await createRequest(values)
    showToast({ type: 'success', message: 'Заявка в поддержку успешно отправлена!' })

    // подтягиваем свежий список, чтобы только что созданная заявка появилась в таблице
    queryClient.invalidateQueries({ queryKey: ['support-requests'] })
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Поддержка</h1>

        <p className="mt-1 text-sm text-gray-500">
          Если у вас возник вопрос или проблема, создайте обращение в службу поддержки.
        </p>
      </div>

      <section className="rounded-2xl border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-6 py-5">
          <h2 className="text-lg font-semibold text-gray-900">Новое обращение</h2>

          <p className="mt-1 text-sm text-gray-500">
            Опишите вашу проблему, и мы постараемся помочь.
          </p>
        </div>

        <FormProvider {...form}>
          <form onSubmit={handleCreateSupportRequest} className="space-y-5 p-6">
            <FormSelect<SupportFormInput>
              name="requestType"
              label="Тип обращения"
              options={requestTypeOptions}
              placeholder="Выберите тип обращения"
            />

            <FormInput<SupportFormInput>
              name="title"
              label="Тема обращения"
              placeholder="Кратко опишите проблему"
            />

            <div className="flex w-full flex-col gap-1.5">
              <label htmlFor="description" className="text-sm font-medium text-gray-800">
                Описание
              </label>

              <textarea
                id="description"
                rows={6}
                placeholder="Подробно опишите вашу проблему или вопрос..."
                {...form.register('description')}
                className={[
                  'w-full resize-none rounded-xl border bg-white px-4 py-3',
                  'text-sm text-gray-900 placeholder:text-gray-400',
                  'transition-all duration-200 outline-none',
                  'focus:ring-2',
                  form.formState.errors.description
                    ? 'border-red-400 focus:border-red-400 focus:ring-red-400/15'
                    : 'border-gray-200 focus:border-orange-500 focus:ring-orange-500/15',
                ].join(' ')}
              />

              {form.formState.errors.description?.message && (
                <span className="text-xs font-medium text-red-500">
                  {form.formState.errors.description.message}
                </span>
              )}
            </div>

            <div className="flex justify-end pt-2">
              <Button
                type="submit"
                variant="blue"
                size="lg"
                // fullWidth={false}
                disabled={form.formState.isSubmitting || isPending}
                isSubmitting={isPending}
                loadingText="Отправляем..."
              >
                Отправить обращение
              </Button>
            </div>
          </form>
        </FormProvider>
      </section>

      <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
        <div className="border-b border-gray-100 px-6 py-5">
          <h2 className="text-lg font-semibold text-gray-900">Мои обращения</h2>

          <p className="mt-1 text-sm text-gray-500">История обращений в службу поддержки.</p>
        </div>

        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="flex min-h-40 items-center justify-center">
              <p className="text-sm text-gray-500">Загрузка обращений...</p>
            </div>
          ) : isError ? (
            <div className="px-6 py-12 text-center">
              <p className="text-sm font-medium text-gray-900">Не удалось загрузить обращения</p>

              <p className="mt-1 text-sm text-gray-500">
                Попробуйте обновить страницу или зайдите позже.
              </p>
            </div>
          ) : (
            <>
              <table className="w-full min-w-200">
                <thead>
                  <tr className="border-b border-gray-100 bg-gray-50/70">
                    <th className="px-6 py-3 text-left text-xs font-medium tracking-wide text-gray-500 uppercase">
                      Обращение
                    </th>

                    <th className="px-6 py-3 text-left text-xs font-medium tracking-wide text-gray-500 uppercase">
                      Тип
                    </th>

                    <th className="px-6 py-3 text-left text-xs font-medium tracking-wide text-gray-500 uppercase">
                      Статус
                    </th>

                    <th className="px-6 py-3 text-left text-xs font-medium tracking-wide text-gray-500 uppercase">
                      Создано
                    </th>

                    <th className="px-6 py-3 text-left text-xs font-medium tracking-wide text-gray-500 uppercase">
                      Обновлено
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-gray-100">
                  {requests.map(request => {
                    const typeLabel =
                      requestTypeLabels[request.request_type] ?? request.request_type
                    const status = statusConfig[request.status] ?? {
                      label: request.status,
                      className: 'bg-gray-50 text-gray-600',
                    }

                    return (
                      <tr key={request.id} className="transition-colors hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div>
                            <p className="text-sm font-medium text-gray-900">{request.title}</p>

                            <p className="mt-0.5 text-xs text-gray-400">#{request.id}</p>
                          </div>
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-600">{typeLabel}</td>

                        <td className="px-6 py-4">
                          <span
                            className={[
                              'inline-flex rounded-full px-3 py-1',
                              'text-xs font-medium',
                              status.className,
                            ].join(' ')}
                          >
                            {status.label}
                          </span>
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-500">
                          {formatDate(request.created_at)}
                        </td>

                        <td className="px-6 py-4 text-sm text-gray-500">
                          {formatDate(request.updated_at)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>

              {requests.length === 0 && (
                <div className="px-6 py-12 text-center">
                  <Ticket className="mx-auto size-8 text-gray-300" />

                  <p className="mt-3 text-sm font-medium text-gray-900">У вас пока нет обращений</p>

                  <p className="mt-1 text-sm text-gray-500">
                    Создайте первое обращение, если вам нужна помощь.
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  )
}

export default SupportPage
