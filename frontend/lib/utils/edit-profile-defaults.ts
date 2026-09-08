import type { Executor } from '@/types'
import type { EditProfileFormInput } from '@/schemas/executor/profile/profileSchema'

export function getEditProfileDefaultValues(executor: Executor | null): EditProfileFormInput {
  const common = {
    name: executor?.name ?? '',
    phone_number: executor?.phone_number ?? '',
    email: executor?.email ?? '',
    image: executor?.image ?? '',
    isNotificationsEnabled: executor?.is_notifications_enabled ?? false,
  }

  switch (executor?.type) {
    case 'supplier':
      return {
        ...common,
        type: 'supplier',
        legal_name: executor.supplier?.legal_name ?? '',
        UNP: executor.supplier?.unp ?? '',
        address: executor.supplier?.address ?? '',
        brands: executor.supplier?.brands ?? [],
      }

    case 'service':
      return {
        ...common,
        type: 'service',
        legal_name: executor.service?.legal_name ?? '',
        UNP: executor.service?.unp ?? '',
        address: executor.service?.address ?? '',
        brands: executor.service?.brands ?? [],
      }

    case 'carrier':
    default:
      return {
        ...common,
        type: 'carrier',
      }
  }
}
