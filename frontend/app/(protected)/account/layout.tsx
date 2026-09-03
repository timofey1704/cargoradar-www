import { Providers } from '@/app/providers/providers'
import ClientAuthProvider from '../../providers/client-auth-provider'

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <ClientAuthProvider>{children}</ClientAuthProvider>
    </Providers>
  )
}
