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

export const getAccountTypeStyles = (accountType: string) => {
  switch (accountType.toLowerCase()) {
    // клиенты
    case 'individual':
      return 'bg-blue-100 text-blue-800'
    case 'legal':
      return 'bg-indigo-100 text-indigo-800'

    // исполнители
    case 'carrier':
      return 'bg-emerald-100 text-emerald-800'
    case 'supplier':
      return 'bg-amber-100 text-amber-800'
    case 'service':
      return 'bg-purple-100 text-purple-800'

    default:
      return 'bg-gray-100 text-gray-600'
  }
}
