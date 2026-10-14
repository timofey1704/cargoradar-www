import React from 'react'

interface CarDetailProps {
  icon: React.ReactNode
  label: string
  value: string
  wide?: boolean
  wrapValue?: boolean
}

function CarDetail({ icon, label, value, wide = false, wrapValue = false }: CarDetailProps) {
  return (
    <div className={wide ? 'col-span-2 min-w-0' : 'min-w-0'}>
      <dt className="flex items-center gap-1.5 text-xs text-gray-500">
        <span className="text-gray-400 [&>svg]:size-3.5">{icon}</span>
        {label}
      </dt>
      <dd
        className={`mt-1 text-sm font-medium text-gray-800 ${wrapValue ? 'break-all' : 'truncate'}`}
      >
        {value}
      </dd>
    </div>
  )
}

export default CarDetail
