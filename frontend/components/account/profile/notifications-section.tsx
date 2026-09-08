import { Bell } from 'lucide-react'
import { useFormContext } from 'react-hook-form'
import type { FieldValues, Path } from 'react-hook-form'

interface NotificationsSectionProps<T extends FieldValues> {
  name: Path<T>
}

function NotificationsSection<T extends FieldValues>({ name }: NotificationsSectionProps<T>) {
  const { register } = useFormContext<T>()

  return (
    <section className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
      <div className="border-b border-gray-100 px-6 py-5">
        <h2 className="text-lg font-semibold text-gray-900">Настройки</h2>
        <p className="mt-1 text-sm text-gray-500">Управляйте настройками вашего аккаунта.</p>
      </div>

      <div className="p-6">
        <label className="flex cursor-pointer items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-gray-50">
              <Bell className="size-5 text-gray-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">Получать уведомления</p>
              <p className="mt-0.5 text-xs text-gray-500">
                Уведомления о заказах и важных событиях.
              </p>
            </div>
          </div>

          <input type="checkbox" {...register(name)} className="size-5 accent-orange-500" />
        </label>
      </div>
    </section>
  )
}

export default NotificationsSection
