'use client'

import { FormProvider } from 'react-hook-form'
import { Ticket } from 'lucide-react'

import { useAppForm } from '@/hooks/use-app-form'
import { FormInput } from '@/components/ui/form-input'
import { FormSelect } from '@/components/ui/form-select'
import { Button } from '@/components/ui/button'
import { supportSchema, type SupportFormInput } from '@/schemas/support/createRequest'
import { useCreateSupportRequest } from '@/hooks/use-create-support-request'
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

const requests = [
  {
    id: 1024,
    title: 'Не получается создать заказ',
    type: 'Техническая проблема',
    status: 'В работе',
    statusClass: 'bg-orange-50 text-orange-600',
    createdAt: '06.09.2026',
    updatedAt: '06.09.2026',
  },
  {
    id: 1023,
    title: 'Вопрос по оплате',
    type: 'Оплата',
    status: 'Закрыто',
    statusClass: 'bg-green-50 text-green-600',
    createdAt: '02.09.2026',
    updatedAt: '03.09.2026',
  },
  {
    id: 1022,
    title: 'Не могу изменить данные профиля',
    type: 'Вопрос по аккаунту',
    status: 'Новое',
    statusClass: 'bg-blue-50 text-blue-600',
    createdAt: '01.09.2026',
    updatedAt: '01.09.2026',
  },
]

const SupportPage = () => {
  const { form } = useAppForm({
    schema: supportSchema,
    defaultValues: {
      requestType: '',
      title: '',
      description: '',
    },
  })

  const { mutate: createRequest, isPending } = useCreateSupportRequest(clientRequest)

  const handleCreateSupportRequest = form.handleSubmit(values => {
    createRequest(values, {
      onSuccess: () => {
        showToast({ type: 'success', message: 'Заявка в поддержку успешно отправлена!' })
      },
    })
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
              {requests.map(request => (
                <tr key={request.id} className="cursor-pointer transition-colors hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{request.title}</p>

                      <p className="mt-0.5 text-xs text-gray-400">#{request.id}</p>
                    </div>
                  </td>

                  <td className="px-6 py-4 text-sm text-gray-600">{request.type}</td>

                  <td className="px-6 py-4">
                    <span
                      className={[
                        'inline-flex rounded-full px-3 py-1',
                        'text-xs font-medium',
                        request.statusClass,
                      ].join(' ')}
                    >
                      {request.status}
                    </span>
                  </td>

                  <td className="px-6 py-4 text-sm text-gray-500">{request.createdAt}</td>

                  <td className="px-6 py-4 text-sm text-gray-500">{request.updatedAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {requests.length === 0 && (
          <div className="px-6 py-12 text-center">
            <Ticket className="mx-auto size-8 text-gray-300" />

            <p className="mt-3 text-sm font-medium text-gray-900">У вас пока нет обращений</p>

            <p className="mt-1 text-sm text-gray-500">
              Создайте первое обращение, если вам нужна помощь.
            </p>
          </div>
        )}
      </section>
    </div>
  )
}

export default SupportPage
