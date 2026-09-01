import type { RegisterFormOutput as ClientRegisterFormOutput } from '@/schemas/auth/register/clientSchema'
import type { RegisterFormOutput as ExecutorRegisterFormOutput } from '@/schemas/auth/register/executorSchema'

type RegisterValues = ClientRegisterFormOutput | ExecutorRegisterFormOutput

function normalizeRegisterPayload(values: RegisterValues) {
  if (!('brands' in values)) {
    return values
  }

  const nextBrands = Array.isArray(values.brands)
    ? values.brands.filter(brand => brand !== 'all')
    : values.brands

  return {
    ...values,
    brands: nextBrands,
  }
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
