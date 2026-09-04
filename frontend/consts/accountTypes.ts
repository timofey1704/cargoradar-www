import { Client, Executor } from '@/types'

interface AccountTypeConfig {
  label: string
  className: string
}

export const ClientAccountTypeConfig: Record<Client['type'], AccountTypeConfig> = {
  individual: {
    label: 'Физ лицо',
    className: 'bg-blue-100 text-blue-700',
  },
  legal: {
    label: 'Юр лицо',
    className: 'bg-purple-100 text-purple-700',
  },
}

export const ExecutorAccountTypeConfig: Record<Executor['type'], AccountTypeConfig> = {
  carrier: {
    label: 'Перевозчик',
    className: 'bg-green-100 text-green-700',
  },
  supplier: {
    label: 'Поставщик',
    className: 'bg-orange-100 text-orange-700',
  },
  service: {
    label: 'СТО',
    className: 'bg-yellow-100 text-yellow-700',
  },
}

// для бекенда: русское название -> ключ типа
export const displayNameToAccountType: Record<string, Client['type']> = Object.fromEntries(
  Object.entries(ClientAccountTypeConfig).map(([type, config]) => [config.label, type])
) as Record<string, Client['type']>

export const displayNameToExecutorAccountType: Record<string, Executor['type']> =
  Object.fromEntries(
    Object.entries(ExecutorAccountTypeConfig).map(([type, config]) => [config.label, type])
  ) as Record<string, Executor['type']>

export function getAccountTypeConfig(accountType: 'client', type: Client['type']): AccountTypeConfig
export function getAccountTypeConfig(
  accountType: 'executor',
  type: Executor['type']
): AccountTypeConfig
export function getAccountTypeConfig(
  accountType: 'client' | 'executor',
  type: Client['type'] | Executor['type']
): AccountTypeConfig {
  return accountType === 'client'
    ? ClientAccountTypeConfig[type as Client['type']]
    : ExecutorAccountTypeConfig[type as Executor['type']]
}
