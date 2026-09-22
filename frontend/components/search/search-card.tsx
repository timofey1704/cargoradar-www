import Link from 'next/link'
import { ArrowRight, Car, MapPin, Star, Wrench, Package } from 'lucide-react'
import type { SearchCardProps, CarrierSearchCardProps, OrganizationSearchCardProps } from '@/types'

function Avatar({ src, fallback }: { src?: string | null; fallback: React.ReactNode }) {
  if (src) {
    return (
      <div className="h-12 w-12 shrink-0 overflow-hidden rounded-full bg-gray-100">
        <img src={src} alt="" className="h-full w-full object-cover" />
      </div>
    )
  }

  return (
    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gray-100 text-gray-400">
      {fallback}
    </div>
  )
}

function Rating({ rating, reviewsCount }: { rating?: number | null; reviewsCount?: number }) {
  if (!rating) {
    return null
  }

  return (
    <div className="flex items-center gap-1.5 text-sm text-gray-500">
      <Star size={14} className="text-orange fill-current" />

      <span className="text-text font-medium">{rating.toFixed(1)}</span>

      {reviewsCount !== undefined && (
        <span>
          · {reviewsCount} {reviewsCount === 1 ? 'отзыв' : 'отзывов'}
        </span>
      )}
    </div>
  )
}

function Tags({ items, max = 4 }: { items: string[]; max?: number }) {
  const visibleItems = items.slice(0, max)
  const remainingCount = items.length - visibleItems.length

  if (!items.length) {
    return null
  }

  return (
    <div className="flex flex-wrap gap-2">
      {visibleItems.map(item => (
        <span
          key={item}
          className="rounded-lg bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600"
        >
          {item}
        </span>
      ))}

      {remainingCount > 0 && (
        <span className="rounded-lg bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-500">
          +{remainingCount}
        </span>
      )}
    </div>
  )
}

function CarrierCard({ executor, vehicle, route, href }: CarrierSearchCardProps) {
  return (
    <Link
      href={href}
      className="group hover:border-orange/40 block rounded-2xl border border-gray-200 bg-white p-5 transition hover:shadow-lg hover:shadow-gray-200/50"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <Avatar src={executor.photoUrl} fallback={<Car size={22} />} />

          <div className="min-w-0">
            <h3 className="text-text truncate font-semibold">{executor.name}</h3>

            <Rating rating={executor.rating} reviewsCount={executor.reviewsCount} />
          </div>
        </div>

        <ArrowRight
          size={20}
          className="group-hover:text-orange shrink-0 text-gray-300 transition group-hover:translate-x-1"
        />
      </div>

      {route && (
        <div className="mt-5 rounded-xl bg-gray-50 p-4">
          <div className="flex gap-3">
            <div className="flex w-4 shrink-0 flex-col items-center pt-1">
              <div className="border-orange h-2.5 w-2.5 rounded-full border-2 bg-white" />

              <div className="my-1 h-8 w-px bg-gray-300" />

              <MapPin size={14} className="text-orange" />
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex min-h-8 items-start">
                <span className="text-text truncate text-sm font-medium">{route.from}</span>
              </div>

              <div className="flex items-start">
                <span className="text-text truncate text-sm font-medium">{route.to}</span>
              </div>
            </div>
          </div>

          {route.comment && (
            <p className="mt-3 border-t border-gray-200 pt-3 text-xs leading-5 text-gray-500">
              {route.comment}
            </p>
          )}
        </div>
      )}

      <div className="mt-5 border-t border-gray-100 pt-5">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gray-100">
            <Car size={18} className="text-gray-500" />
          </div>

          <div className="min-w-0">
            <p className="text-text truncate text-sm font-semibold">
              {vehicle.brand} {vehicle.model}
            </p>

            <div className="mt-1 flex flex-wrap gap-x-2 text-xs text-gray-500">
              <span>{vehicle.cargoCapacity.toLocaleString('ru-RU')} кг</span>

              {vehicle.volumeCapacity && (
                <>
                  <span>·</span>
                  <span>{vehicle.volumeCapacity} м³</span>
                </>
              )}

              {vehicle.carType && (
                <>
                  <span>·</span>
                  <span>{vehicle.carType}</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {(route?.price || vehicle.pricePerKm) && (
        <div className="mt-5 flex items-end justify-between border-t border-gray-100 pt-4">
          <span className="text-sm text-gray-500">
            {route?.price ? 'Стоимость заказа' : 'Стоимость за км'}
          </span>

          <span className="text-text text-lg font-bold">
            {(route?.price ?? vehicle.pricePerKm)?.toLocaleString('ru-RU')} BYN
          </span>
        </div>
      )}
    </Link>
  )
}

function OrganizationCard({ type, organization, href }: OrganizationSearchCardProps) {
  const isService = type === 'service'

  return (
    <Link
      href={href}
      className="group hover:border-orange/40 block rounded-2xl border border-gray-200 bg-white p-5 transition hover:shadow-lg hover:shadow-gray-200/50"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <Avatar
            src={organization.photoUrl}
            fallback={isService ? <Wrench size={22} /> : <Package size={22} />}
          />

          <div className="min-w-0">
            <h3 className="text-text truncate font-semibold">{organization.legalName}</h3>

            <Rating rating={organization.rating} reviewsCount={organization.reviewsCount} />
          </div>
        </div>

        <ArrowRight
          size={20}
          className="group-hover:text-orange shrink-0 text-gray-300 transition group-hover:translate-x-1"
        />
      </div>

      <div className="mt-5 flex items-start gap-2 text-sm text-gray-500">
        <MapPin size={17} className="mt-0.5 shrink-0 text-gray-400" />

        <span>{organization.address}</span>
      </div>

      <div className="mt-5 border-t border-gray-100 pt-5">
        <p className="mb-3 text-xs font-medium tracking-wide text-gray-400 uppercase">
          {isService ? 'Марки автомобилей' : 'Запчасти для'}
        </p>

        <Tags items={organization.brands} />
      </div>
    </Link>
  )
}

export function SearchCard(props: SearchCardProps) {
  if (props.type === 'carrier') {
    return <CarrierCard {...props} />
  }

  return <OrganizationCard {...props} />
}
// ### использование

// carrier:
// <SearchCard
//   type="carrier"
//   href={`/search/carrier/${executor.id}`}
//   executor={{
//     id: executor.id,
//     name: executor.name,
//     photoUrl: executor.photo_url,
//     rating: executor.rating,
//     reviewsCount: executor.reviews_count,
//   }}
//   vehicle={{
//     type: vehicle.type,
//     brand: vehicle.brand,
//     model: vehicle.model,
//     cargoCapacity: vehicle.cargo_capacity,
//     volumeCapacity: vehicle.volume_capacity,
//     carType: vehicle.car_type,
//     manufactureYear: vehicle.manufacture_year,
//     photoUrl: vehicle.photo_url,
//     pricePerKm: vehicle.price_per_km,
//   }}
//   route={{
//     from: 'Минск',
//     to: 'Брест',
//     comment: 'Нужна перевозка груза до 20 тонн',
//     price: 450,
//   }}
// />

// сто:

// <SearchCard
//   type="service"
//   href={`/search/service/${service.executor_id}`}
//   organization={{
//     id: service.executor_id,
//     legalName: service.legal_name,
//     address: service.address,
//     brands: service.brands.map((item) => item.brand),
//     photoUrl: service.photo_url,
//     rating: service.rating,
//     reviewsCount: service.reviews_count,
//   }}
// />

// Для поставщика:

// <SearchCard
//   type="supplier"
//   href={`/search/supplier/${supplier.executor_id}`}
//   organization={{
//     id: supplier.executor_id,
//     legalName: supplier.legal_name,
//     address: supplier.address,
//     brands: supplier.brands.map((item) => item.brand),
//     photoUrl: supplier.photo_url,
//     rating: supplier.rating,
//     reviewsCount: supplier.reviews_count,
//   }}
// />
