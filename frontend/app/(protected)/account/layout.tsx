import ClientAuthProvider from '../../providers/client-auth-provider'

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  return <ClientAuthProvider>{children}</ClientAuthProvider>
}
