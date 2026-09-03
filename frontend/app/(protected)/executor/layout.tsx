import { Providers } from '@/app/providers/providers'
import ExecutorAuthProvider from '../../providers/executor-auth-provider'

export default function ExecutorLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <ExecutorAuthProvider>{children}</ExecutorAuthProvider>
    </Providers>
  )
}
