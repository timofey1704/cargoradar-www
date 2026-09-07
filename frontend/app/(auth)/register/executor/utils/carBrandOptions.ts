import { CAR_BRAND_NAMES } from '@/consts/carBrands'
import { CarBrands } from '@/consts/carBrands'

export const carBrandOptions = Object.entries(CAR_BRAND_NAMES)
  .filter(([value]) => value !== CarBrands.all)
  .map(([value, label]) => ({
    value,
    label,
  }))

export const BRAND_OPTIONS = Object.entries(CAR_BRAND_NAMES).map(([value, label]) => ({
  value,
  label,
}))
