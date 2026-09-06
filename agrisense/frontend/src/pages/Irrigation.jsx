import { useState } from 'react'
import Card from '../components/Card'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { irrigationApi } from '../api/services'
import { getProfile } from '../utils/farmerProfile'
import { useTranslation } from '../context/LanguageContext'

const DECISION_LABELS = {
  irrigate_now: { text: 'Irrigate now', accent: 'sky' },
  wait: { text: 'Wait', accent: 'wheat' },
  reduce: { text: 'Reduce irrigation', accent: 'clay' },
  rain_sufficient: { text: 'Rain may be sufficient', accent: 'sky' },
  insufficient_data: { text: 'Not enough data', accent: 'soil' },
}

const STAGES = [
  { value: '', label: 'Not sure / skip' },
  { value: 'sowing', label: 'Sowing' },
  { value: 'vegetative', label: 'Vegetative growth' },
  { value: 'flowering', label: 'Flowering' },
  { value: 'grain_filling', label: 'Grain filling' },
  { value: 'tuber_bulking', label: 'Tuber bulking (potato etc.)' },
  { value: 'fruit_set', label: 'Fruit set (tomato etc.)' },
  { value: 'maturity', label: 'Maturity / near harvest' },
]

export default function Irrigation() {
  const { t } = useTranslation()
  const profile = getProfile()
  const [crop, setCrop] = useState(profile.current_crop || '')
  const [stage, setStage] = useState('')
  const [moisture, setMoisture] = useState('')
  const [recentRainfall, setRecentRainfall] = useState('')
  const [locationName, setLocationName] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        crop: crop || undefined,
        crop_stage: stage || undefined,
        soil_moisture: moisture ? parseFloat(moisture) : undefined,
        recent_rainfall_mm: recentRainfall ? parseFloat(recentRainfall) : undefined,
        location_name: locationName || undefined,
        farmer_profile: getProfile(),
      }
      const res = await irrigationApi.advise(payload)
      setResult(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const label = result ? DECISION_LABELS[result.decision] : null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-foliage-900">{t('irrigationPage.title')}</h1>
        <p className="text-ink/70 mt-1">{t('irrigationPage.subtitle')}</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Crop</label>
            <input value={crop} onChange={(e) => setCrop(e.target.value)}
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Growth stage</label>
            <select value={stage} onChange={(e) => setStage(e.target.value)}
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm bg-white">
              {STAGES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1">
              Soil moisture (%) <span className="text-ink/40 font-normal">({t('common.optional')})</span>
            </label>
            <input type="number" step="any" value={moisture} onChange={(e) => setMoisture(e.target.value)}
              placeholder="Don't know? Leave blank"
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-medium text-ink mb-1">
              Recent rainfall (mm) <span className="text-ink/40 font-normal">({t('common.optional')})</span>
            </label>
            <input type="number" step="any" value={recentRainfall} onChange={(e) => setRecentRainfall(e.target.value)}
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none" />
          </div>
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-ink mb-1">
              Check a different location? <span className="text-ink/40 font-normal">(leave blank to use your saved farm location)</span>
            </label>
            <input value={locationName} onChange={(e) => setLocationName(e.target.value)}
              placeholder="e.g. Kalka"
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none" />
          </div>
          {error && <div className="sm:col-span-2"><ErrorBanner message={error} /></div>}
          <div className="sm:col-span-2">
            <button type="submit" disabled={loading}
              className="bg-foliage-800 text-white rounded-xs px-6 py-2.5 text-sm font-medium hover:bg-foliage-900 disabled:opacity-60">
              {loading ? 'Checking…' : 'Get Advice'}
            </button>
          </div>
        </form>
      </Card>

      {loading && <LoadingSpinner />}

      {result && (
        <Card accent={label.accent}>
          <h3 className="font-display text-xl text-foliage-900 mb-1">{label.text}</h3>
          {result.location_used && (
            <p className="text-xs text-ink/50 mb-2">For: {result.location_used}</p>
          )}
          <p className="text-sm text-ink/80 whitespace-pre-line">{result.reasoning}</p>
          {result.weather_used?.forecast && (
            <div className="mt-4 pt-4 border-t border-foliage-100 grid grid-cols-3 gap-3">
              {result.weather_used.forecast.slice(0, 3).map((d) => (
                <div key={d.date} className="text-center text-xs">
                  <p className="text-ink/60">{new Date(d.date).toLocaleDateString([], { weekday: 'short' })}</p>
                  <p className="font-medium text-sky-500 mt-1">{d.rain_probability_pct}% rain</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
