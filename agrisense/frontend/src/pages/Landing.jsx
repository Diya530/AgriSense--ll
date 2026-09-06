import { Link } from 'react-router-dom'
import { Sprout, CloudSun, MessageCircle, Leaf } from 'lucide-react'
import Logo from '../components/Logo'
import { useTranslation } from '../context/LanguageContext'

const FEATURES = [
  { icon: MessageCircle, title: 'Ask anything, in your language', text: 'Chat in English, Hindi, Punjabi and more. Real answers, not guesses.' },
  { icon: CloudSun, title: 'Real weather, not predictions from thin air', text: 'Live forecasts before every spray or irrigation decision.' },
  { icon: Sprout, title: 'Crop & soil guidance', text: 'Recommendations grounded in your actual soil numbers and conditions.' },
  { icon: Leaf, title: 'Spot plant problems early', text: 'Upload a photo of a struggling crop and get an honest read on what you\'re seeing.' },
]

export default function Landing() {
  const { t } = useTranslation()
  return (
    <div className="min-h-screen bg-canvas">
      <header className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between">
        <Logo size={30} />
        <Link to="/dashboard" className="px-4 py-2 text-sm font-medium bg-foliage-800 text-white rounded-xs hover:bg-foliage-900">
          Open AgriSense
        </Link>
      </header>

      <section className="max-w-6xl mx-auto px-6 pt-12 pb-20 grid md:grid-cols-2 gap-10 items-center">
        <div>
          <h1 className="font-display text-5xl md:text-6xl leading-[1.05] text-foliage-900">
            {t('landing.tagline')}
          </h1>
          <p className="mt-6 text-lg text-ink/80 max-w-md">
            AgriSense combines a real weather feed, your soil numbers, and an AI
            advisor that answers in your language — so every recommendation is
            grounded in what's actually happening on your field, not a guess.
          </p>
          <Link
            to="/dashboard"
            className="inline-block mt-8 px-6 py-3 bg-wheat-500 text-foliage-900 font-medium rounded-xs hover:bg-wheat-300 transition-colors"
          >
            {t('landing.cta')}
          </Link>
          <p className="mt-3 text-sm text-ink/50">
            You can add your farm details anytime from Profile — it's optional.
          </p>
        </div>
        <div className="bg-white rounded-xs shadow-soft border border-foliage-100 p-6">
          <div className="space-y-4">
            <div className="bg-sky-100 rounded-xs p-4 text-sm text-foliage-900">
              <strong>You:</strong> Should I spray pesticide tomorrow?
            </div>
            <div className="bg-foliage-50 rounded-xs p-4 text-sm text-foliage-900">
              <strong>AgriSense:</strong> Tomorrow's forecast shows 70% rain chance
              and 22 km/h wind in your area — spraying now would likely wash off
              and drift. I'd wait until conditions settle, probably the day after.
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-24 grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {FEATURES.map(({ icon: Icon, title, text }) => (
          <div key={title} className="bg-white rounded-xs border border-foliage-100 p-5">
            <Icon size={22} className="text-foliage-700 mb-3" strokeWidth={1.75} />
            <h3 className="font-display text-base text-foliage-900 mb-1.5">{title}</h3>
            <p className="text-sm text-ink/70">{text}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
