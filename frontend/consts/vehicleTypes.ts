export const VehicleTypes = {
  truck: 'truck',
  special_equipment: 'special_equipment',
  towtruck: 'towtruck',
} as const

export type VehicleType = (typeof VehicleTypes)[keyof typeof VehicleTypes]

export const VehicleTypesNames: Record<VehicleType, string> = {
  truck: 'Грузовик',
  special_equipment: 'Спецтехника',
  towtruck: 'Эвакуатор',
}

export const CarTypes = {
  sedan: 'sedan',
  hatchback: 'hatchback',
  coupe: 'coupe',
  convertible: 'convertible',
  suv: 'suv',
  crossover: 'crossover',
  minivan: 'minivan',
  van: 'van',
  pickup: 'pickup',
} as const

export type CarType = (typeof CarTypes)[keyof typeof CarTypes]

export const CarTypesNames: Record<CarType, string> = {
  sedan: 'Седан',
  hatchback: 'Хэтчбек',
  coupe: 'Купе',
  convertible: 'Кабриолет',
  suv: 'Внедорожник',
  crossover: 'Кроссовер',
  minivan: 'Минивэн',
  van: 'Фургон',
  pickup: 'Пикап',
}
