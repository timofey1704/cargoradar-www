'use client'

import dynamic from 'next/dynamic'
import Image from 'next/image'
import { useState } from 'react'
import { CalendarDays, MapPin, Package, Truck } from 'lucide-react'

import type { SearchFeedItem } from '@/lib/search/get-feed'
import { createOrderOffer } from '@/lib/api/chat'
import { formatDateTime } from '@/lib/utils/datetime-formatter'
import { Button } from '@/components/ui/button'
import Modal from '@/components/ui/modal'
import { getGoogleMapsUrl, getYandexMapsUrl } from '@/lib/utils/map-links'

const RequestRouteMap = dynamic(
  () => import('@/components/map/route-map').then(module => module.RouteMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-72 items-center justify-center rounded-xl bg-gray-100 text-sm text-gray-500">
        Загружаем карту...
      </div>
    ),
  }
)

export function RequestOfferAction({
  item,
}: {
  item: Extract<SearchFeedItem, { kind: 'request' }>
}) {
  const request = item.request
  const [isOpen, setIsOpen] = useState(false)
  const [price, setPrice] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [created, setCreated] = useState(false)

  if (!request) return null

  const origin = item.map_points[0] ?? null
  const destination = item.map_points[1] ?? null
  const formattedDate = new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(request.loading_date))

  const open = () => {
    setError(null)
    setCreated(false)
    setIsOpen(true)
  }

  const submitOffer = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await createOrderOffer(item.id, { price: Number(price) })
      setCreated(true)
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message === 'UNAUTHORIZED'
            ? 'Войдите в аккаунт исполнителя, чтобы отправить предложение.'
            : submitError.message
          : 'Не удалось отправить предложение. Попробуйте ещё раз.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <Button type="button" variant="blue" size="md" onClick={open}>
        Откликнуться
      </Button>

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title={`Заявка #${item.id}`}>
        <div className="max-h-[calc(100dvh-6rem)] space-y-6 overflow-y-auto p-4 sm:p-6">
          <section>
            <h3 className="text-text text-base font-semibold">Информация о перевозке</h3>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <RouteAddress label="Откуда" value={request.origin_address} />
              <RouteAddress label="Куда" value={request.destination_address} />
              <DetailItem icon={<Package size={17} />} label="Груз">
                {request.cargo_type}
                <span className="mt-1 block text-xs font-normal text-gray-500">
                  {request.weight_kg.toLocaleString('ru-RU')} кг
                  {request.volume_m3 !== null &&
                    ` · ${request.volume_m3.toLocaleString('ru-RU')} м³`}
                </span>
              </DetailItem>
              <DetailItem icon={<CalendarDays size={17} />} label="Дата погрузки">
                {formattedDate}
              </DetailItem>
              {request.vehicle_type && (
                <DetailItem icon={<Truck size={17} />} label="Транспорт">
                  {request.vehicle_type}
                </DetailItem>
              )}
              <DetailItem icon={<Package size={17} />} label="Бюджет клиента">
                {request.budget === null
                  ? 'Не указан'
                  : `${request.budget.toLocaleString('ru-RU')} BYN`}
              </DetailItem>
            </div>
            {request.comment && (
              <div className="mt-4 border-t border-gray-100 pt-4">
                <p className="text-xs text-gray-400">Комментарий</p>
                <p className="text-text mt-1 text-sm whitespace-pre-wrap">{request.comment}</p>
              </div>
            )}
            <p className="mt-4 text-xs text-gray-400">
              Опубликовано {formatDateTime(item.created_at)}
            </p>
          </section>

          <section>
            <h3 className="text-text mb-3 text-base font-semibold">Маршрут</h3>
            <RequestRouteMap
              origin={origin ? { latitude: origin.latitude, longitude: origin.longitude } : null}
              destination={
                destination
                  ? { latitude: destination.latitude, longitude: destination.longitude }
                  : null
              }
            />
            {origin && destination && (
              <div className="mt-3 flex flex-wrap gap-3 lg:justify-around">
                <a
                  href={getYandexMapsUrl(origin, destination)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex h-10 items-center rounded-lg border border-gray-300 px-4 text-sm font-medium hover:bg-gray-50"
                >
                  <Image
                    src="/icons/Yandex_icon.webp"
                    alt="Яндекс Карты"
                    width={32}
                    height={32}
                    className="mr-2"
                  />
                  Открыть в Яндекс Картах
                </a>
                <a
                  href={getGoogleMapsUrl(origin, destination)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex h-10 items-center rounded-lg border border-gray-300 px-4 text-sm font-medium hover:bg-gray-50"
                >
                  <Image
                    src="/icons/Google_icon.svg"
                    alt="Google Maps"
                    width={26}
                    height={26}
                    className="mr-2"
                  />
                  Open in Google Maps
                </a>
              </div>
            )}
          </section>

          <section className="border-t border-gray-100 pt-5">
            {created ? (
              <div className="rounded-lg border border-green-200 bg-green-50 p-4">
                <p className="font-semibold text-green-800">Предложение отправлено</p>
                <p className="mt-1 text-sm text-green-700">Оно появилось в беседе с заказчиком.</p>
              </div>
            ) : (
              <form className="space-y-4" onSubmit={submitOffer}>
                <label className="block">
                  <span className="text-text text-sm font-medium">Ваша цена, BYN</span>
                  <span className="relative mt-2 block">
                    <input
                      type="number"
                      min="0.01"
                      step="0.01"
                      required
                      value={price}
                      onChange={event => setPrice(event.target.value)}
                      placeholder="Например, 450"
                      className="h-12 w-full rounded-lg border border-gray-300 bg-white px-3 pr-14 text-sm transition outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
                    />
                    <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-sm text-gray-400">
                      BYN
                    </span>
                  </span>
                </label>

                {error && (
                  <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                    {error}
                  </p>
                )}

                <Button type="submit" variant="orange" size="md" isSubmitting={isSubmitting}>
                  {isSubmitting ? 'Отправляем...' : 'Создать предложение'}
                </Button>
              </form>
            )}
          </section>
        </div>
      </Modal>
    </>
  )
}

function RouteAddress({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-3">
      <MapPin size={18} className="text-orange mt-0.5 shrink-0" />
      <div className="min-w-0">
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-text mt-1 text-sm font-medium">{value}</p>
      </div>
    </div>
  )
}

function DetailItem({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode
  label: string
  children: React.ReactNode
}) {
  return (
    <div className="flex gap-3">
      <span className="mt-0.5 shrink-0 text-gray-400">{icon}</span>
      <div className="min-w-0">
        <p className="text-xs text-gray-400">{label}</p>
        <p className="text-text mt-1 text-sm font-medium">{children}</p>
      </div>
    </div>
  )
}
