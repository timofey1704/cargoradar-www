import { Providers } from '@/app/providers/providers'

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return <Providers>{children}</Providers>
}
