import Header from '@/components/home/header'
import Footer from '@/components/home/footer'
import { Providers } from '@/app/providers/providers'
import SessionProvider from '@/app/providers/session-provider'

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <SessionProvider>
        <Header />
        {children}
        <Footer />
      </SessionProvider>
    </Providers>
  )
}
