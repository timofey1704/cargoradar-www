export function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Без даты'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Без даты'
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(date)
}
