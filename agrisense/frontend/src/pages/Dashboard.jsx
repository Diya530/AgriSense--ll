import { useEffect, useState } from 'react'
import { CloudSun, Sprout, FlaskConical, Droplets, AlertTriangle } from 'lucide-react'
import Card from '../components/Card'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { weatherApi } from '../api/services'
import { getProfile, hasLocation } from '../utils/farmerProfile'
import { useTranslation } from '../context/LanguageContext'

export default function Dashboard() {
  const { t } = useTranslation()
  const [profile] = useState(() => getProfile())
  const [weather, setWeather] = useState(null)
  const [weatherError, setWeatherError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!hasLocation(profile)) {
      setLoading(false)
      return
    }
    weatherApi.get({ latitude: profile.latitude, longitude: profile.longitude, days: 3 })
      .then((res) => { setWeather(res.data); setWeatherError(null) })
      .catch((err) => setWeatherError(err.message))
      .finally(() => setLoading(false))
  }, [profile])

  if (loading) return <LoadingSpinner label="Loading your dashboard…" />

  const alerts = []
  if (weather?.current) {
    if ((weather.forecast?.[0]?.rain_probability_pct ?? 0) >= 70) {
      alerts.push({ text: 'Heavy rain expected today — hold off on spraying or irrigation.' })
    }
    if (weather.current.temperature_c >= 38) {
      alerts.push({ text: 'High temperature today — monitor crops for heat stress.' })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-foliage-900">
          {profile?.name ? `${t('dashboard.welcomeBack')}, ${profile.name}` : t('dashboard.welcome')}
        </h1>
        <p className="text-ink/70 mt-1">{t('dashboard.subtitle')}</p>
      </div>

      {!profile?.current_crop && (
        <ErrorBanner message={t('dashboard.incompleteProfile')} />
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <Card title={t('dashboard.todayWeather')} accent="sky" icon={CloudSun}>
          {!hasLocation(profile) ? (
            <p className="text-sm text-ink/60">Set your location in Profile to see live weather.</p>
          ) : weatherError ? (
            <ErrorBanner message={weatherError} />
          ) : weather?.current ? (
            <div className="space-y-1 text-sm">
              <p className="text-3xl font-display text-foliage-900">{Math.round(weather.current.temperature_c)}°C</p>
              <p className="text-ink/70">{weather.current.description}</p>
              <p className="text-ink/70">Humidity: {weather.current.humidity_pct}%</p>
              <p className="text-ink/70">Rain chance: {weather.forecast?.[0]?.rain_probability_pct ?? '—'}%</p>
              {weather.is_cached && <p className="text-xs text-clay-400 mt-2">Showing cached data ({weather.source})</p>}
            </div>
          ) : (
            <p className="text-sm text-ink/60">Weather unavailable right now.</p>
          )}
        </Card>

        <Card title={t('dashboard.currentCrop')} accent="foliage" icon={Sprout}>
          {profile?.current_crop ? (
            <div className="text-sm space-y-1">
              <p className="text-lg font-display text-foliage-900">{profile.current_crop}</p>
              <p className="text-ink/70">Land area: {profile.land_area_acres ?? '—'} acres</p>
              <p className="text-ink/70">Soil type: {profile.soil_type || 'Not set'}</p>
            </div>
          ) : (
            <p className="text-sm text-ink/60">No crop set yet. Add one in your Profile.</p>
          )}
        </Card>

        <Card title={t('dashboard.soilStatus')} accent="soil" icon={FlaskConical}>
          <p className="text-sm text-ink/60">
            Run a Soil Analysis to see your soil status here — results aren't saved between
            visits in this version, so check that page directly for the latest result.
          </p>
        </Card>

        <Card title={t('dashboard.irrigation')} accent="sky" icon={Droplets}>
          <p className="text-sm text-ink/60">
            Visit Irrigation Advisor for a fresh recommendation based on today's forecast.
          </p>
        </Card>

        <Card title={t('dashboard.alerts')} accent="clay" icon={AlertTriangle} className="sm:col-span-2 lg:col-span-1">
          {alerts.length > 0 ? (
            <ul className="text-sm space-y-2">
              {alerts.map((a, i) => (
                <li key={i} className="text-ink/80">• {a.text}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-ink/60">{t('dashboard.noAlerts')}</p>
          )}
        </Card>
      </div>
    </div>
  )
}
