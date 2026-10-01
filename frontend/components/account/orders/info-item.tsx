import type { ReactNode } from 'react'

interface InfoItemProps {
  icon: ReactNode
  label: string
  value: string
  secondary?: string
}

function InfoItem({ icon, label, value, secondary }: InfoItemProps) {
  return (
    <div className="flex gap-3">
      <div className="mt-0.5 shrink-0 text-gray-400">{icon}</div>

      <div className="min-w-0">
        <p className="text-xs text-gray-400">{label}</p>

        <p className="text-text mt-1 truncate text-sm font-medium">{value}</p>

        {secondary && <p className="mt-1 text-xs text-gray-500">{secondary}</p>}
      </div>
    </div>
  )
}

export default InfoItem
