import { LoaderCircle } from 'lucide-react'

interface LoaderProps {
  size?: number
  className?: string
}

export function Loader({ size = 24, className = '' }: LoaderProps) {
  return (
    <LoaderCircle
      size={size}
      className={`animate-spin ${className}`}
      aria-label="Загрузка"
      role="status"
    />
  )
}
