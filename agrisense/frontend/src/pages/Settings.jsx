import { Link } from 'react-router-dom'
import Card from '../components/Card'
import { useTranslation } from '../context/LanguageContext'

export default function Settings() {
  const { t } = useTranslation()
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-foliage-900">{t('settings.title')}</h1>
        <p className="text-ink/70 mt-1">{t('settings.subtitle')}</p>
      </div>

      <Card title="Farm Details">
        <p className="text-sm text-ink/70 mb-4">
          Your name, location, language, crop, and soil type are managed on the
          Farmer Profile page and are used to personalize the dashboard and chatbot.
        </p>
        <Link
          to="/profile"
          className="inline-block text-sm font-medium bg-foliage-800 text-white rounded-xs px-4 py-2 hover:bg-foliage-900"
        >
          Edit Farmer Profile
        </Link>
      </Card>

      <Card title="About AgriSense">
        <p className="text-sm text-ink/70">
          AgriSense combines a live weather feed, an AI advisor, and a curated
          agricultural knowledge base to give grounded, honest farming guidance.
          It will always tell you when live data isn't available rather than guess.
        </p>
      </Card>
    </div>
  )
}
