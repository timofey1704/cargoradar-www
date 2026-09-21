import { Hero, HowItWorks, Services, Benefits, FAQ, CTA } from '@/components/home'

const HomePage = () => {
  return (
    <main className="overflow-hidden">
      <Hero />
      <HowItWorks id="how-it-works" />
      <Services />
      <Benefits />
      <FAQ id="faq" />
      <CTA />
    </main>
  )
}

export default HomePage
