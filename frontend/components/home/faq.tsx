import Accordion from '../ui/accordion'
import { getFaq } from '@/lib/main/get-faqs'

interface FAQProps {
  id: string
}

const FAQ: React.FC<FAQProps> = async ({ id }) => {
  const faq = await getFaq()

  return (
    <section className="bg-[#f7f7f5] py-20 sm:py-24 lg:py-32" id={id}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10 max-w-2xl">
          <span className="text-orange text-sm font-semibold">FAQ</span>

          <h2 className="text-text mt-3">Часто задаваемые вопросы</h2>

          <p className="mt-4 text-base leading-7 text-gray-500">
            Ответы на основные вопросы о работе CargoRadar.
          </p>
        </div>

        <div className="space-y-3 sm:space-y-4">
          {faq.map(item => (
            <Accordion key={item.id} title={item.title} content={item.content} />
          ))}
        </div>
      </div>
    </section>
  )
}

export default FAQ
