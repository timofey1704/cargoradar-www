import { Client, Executor } from '@/types'

export const ClientAccountTypeToDisplayName = {
  individual: 'individual',
  legal: 'legal',
} as const

// для бекенда
export const displayNameToAccountType: Record<string, keyof typeof ClientAccountTypeToDisplayName> =
  {
    'Физ лицо': 'individual',
    'Юр лицо': 'legal',
  }

export const ExecutorAccountTypeToDisplayName = {
  carrier: 'carrier',
  supplier: 'supplier',
  service: 'service',
} as const

// для бекенда
export const displayNameToExecutorAccountType: Record<
  string,
  keyof typeof ExecutorAccountTypeToDisplayName
> = {
  Перевозчик: 'carrier',
  Поставщик: 'supplier',
  СТО: 'service',
}

export function getAccountTypeStyles(
  accountType: 'client' | 'executor',
  type: Client['type'] | Executor['type']
): string {
  if (accountType === 'client') {
    const clientStyles: Record<Client['type'], string> = {
      individual: 'bg-blue-100 text-blue-700',
      legal: 'bg-purple-100 text-purple-700',
    }
    return clientStyles[type as Client['type']]
  }

  const executorStyles: Record<Executor['type'], string> = {
    carrier: 'bg-green-100 text-green-700',
    supplier: 'bg-orange-100 text-orange-700',
    service: 'bg-yellow-100 text-yellow-700',
  }
  return executorStyles[type as Executor['type']]
}
