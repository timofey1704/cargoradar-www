import { apiRequest } from '@/lib/api'
import type { CarFormOutput } from '@/schemas/car/carSchema'
import type { Car } from '@/types/car'

export type VehicleUpdatePayload = Pick<Car, 'cargo_capacity' | 'volume_capacity' | 'license_plate'>

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

export async function updateExecutorVehicle(vehicleId: number, data: VehicleUpdatePayload) {
  return apiRequest<Car>(`/executor/vehicles/${vehicleId}`, {
    method: 'PATCH',
    body: data,
  })
}

export async function deleteExecutorVehicle(vehicleId: number) {
  return apiRequest<void>(`/executor/vehicles/${vehicleId}`, {
    method: 'DELETE',
  })
}
