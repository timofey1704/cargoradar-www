export function objectToSelectOptions<T extends Record<string, string>>(object: T) {
  return Object.entries(object).map(([value, label]) => ({
    value,
    label,
  }))
}
