import { Toaster } from 'react-hot-toast'
import AuthLayout from '@/components/layouts/auth-layout'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CargoRadar - Войти в систему',
  description:
    'Ищите перевозчиков и грузы на CargoRadar. Платформа для эффективного взаимодействия между грузоотправителями и перевозчиками.',
}
export default function AuthGroupLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthLayout>
      <Toaster />
      {children}
    </AuthLayout>
  )
}
