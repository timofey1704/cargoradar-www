import { apiRequest } from '@/lib/api'
import type { CarFormOutput } from '@/schemas/car/carSchema'

export async function createExecutorVehicles(cars: CarFormOutput[]) {
  const payload = cars.map(car => {
    const vehicle = { ...car }
    delete vehicle.photo
    return vehicle
  })

  return apiRequest('/executor/vehicles', {
    method: 'POST',
    body: payload,
  })
}
