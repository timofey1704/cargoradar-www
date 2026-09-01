import ExecutorAuthProvider from '../../providers/executor-auth-provider'

export default function ExecutorLayout({ children }: { children: React.ReactNode }) {
  return <ExecutorAuthProvider>{children}</ExecutorAuthProvider>
}
