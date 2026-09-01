import type { RegisterFormOutput as ClientRegisterFormOutput } from '@/schemas/auth/register/clientSchema'
import type { RegisterFormOutput as ExecutorRegisterFormOutput } from '@/schemas/auth/register/executorSchema'

type RegisterValues = ClientRegisterFormOutput | ExecutorRegisterFormOutput

function normalizeRegisterPayload(values: RegisterValues): Record<string, unknown> {
  // клиентская регистрация — отправляем как есть
  if (!('type' in values)) {
    return { ...values }
  }

  const normalized: Record<string, unknown> = { ...values }

  // carrier: JSON.stringify не сериализует File (photo),
  // а отдельного эндпоинта для загрузки фото пока нет — убираем поле.
  if (normalized.type === 'carrier' && Array.isArray(normalized.cars)) {
    normalized.cars = normalized.cars.map(car => {
      const { photo: _photo, ...rest } = car as { photo?: File } & Record<string, unknown>
      return rest
    })
  }

  // supplier / service: бэкенд ожидает вложенный объект профиля
  if (normalized.type === 'supplier' || normalized.type === 'service') {
    const profile: Record<string, unknown> = {}

    if (typeof normalized.legal_name === 'string') {
      profile.legal_name = normalized.legal_name
    }

    if (typeof normalized.UNP === 'string') {
      profile.unp = normalized.UNP
    }

    if (normalized.type === 'supplier' && typeof normalized.pickup_point === 'string') {
      profile.address = normalized.pickup_point
    }

    if (normalized.type === 'service' && typeof normalized.service_address === 'string') {
      profile.address = normalized.service_address
    }

    // марки для СТО: «все марки» (all) — валидное значение само по себе.
    // all убираем только если выбраны конкретные марки; если конкретных марок
    // нет (в т.ч. выбрано только all или ничего) — отправляем ['all'].
    if (normalized.type === 'service' && Array.isArray(normalized.brands)) {
      const brands = normalized.brands.filter((brand): brand is string => typeof brand === 'string')
      const hasSpecific = brands.some(brand => brand !== 'all')
      profile.brands = hasSpecific ? brands.filter(brand => brand !== 'all') : ['all']
    }

    delete normalized.legal_name
    delete normalized.UNP
    delete normalized.pickup_point
    delete normalized.service_address
    if ('brands' in normalized) {
      delete normalized.brands
    }

    normalized[normalized.type] = profile
  }

  return normalized
}

async function registerRequest(values: RegisterValues, url: string) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(normalizeRegisterPayload(values)),
  })

  if (!response.ok) {
    throw new Error('Не удалось выполнить регистрацию')
  }

  return response.json()
}

export async function clientRegister(values: RegisterValues) {
  return registerRequest(values, `${process.env.NEXT_PUBLIC_API_URL}/client/auth/register`)
}

export async function executorRegister(values: RegisterValues) {
  return registerRequest(values, `${process.env.NEXT_PUBLIC_API_URL}/executor/auth/register`)
}
