import { apiRequest } from '@/lib/api'
import type { CarFormOutput } from '@/schemas/car/carSchema'
import type { Car } from '@/types/car'

export type VehicleUpdatePayload = Pick<Car, 'cargo_capacity' | 'volume_capacity' | 'license_plate'>

export async function createExecutorVehicles(cars: CarFormOutput[]) {
  const payload = cars.map(car => {
    const vehicle = { ...car }
    delete vehicle.photos
    return vehicle
  })

  const created = await apiRequest<Car[]>('/executor/vehicles', {
    method: 'POST',
    body: payload,
  })

  let photoUploadFailedCount = 0
  await Promise.all(
    created.map(async (vehicle, index) => {
      const photos = cars[index]?.photos ?? []
      if (photos.length === 0) return

      try {
        await uploadExecutorVehiclePhotos(vehicle.id, photos)
      } catch {
        photoUploadFailedCount += 1
      }
    })
  )

  return { cars: created, photoUploadFailedCount }
}

export async function uploadExecutorVehiclePhotos(vehicleId: number, photos: File[]) {
  const body = new FormData()
  photos.forEach(photo => body.append('photos', photo))

  return apiRequest<Car>(`/executor/vehicles/${vehicleId}/photos`, {
    method: 'POST',
    body,
  })
}

export async function deleteExecutorVehiclePhoto(vehicleId: number, photoId: number) {
  return apiRequest<void>(`/executor/vehicles/${vehicleId}/photos/${photoId}`, {
    method: 'DELETE',
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
