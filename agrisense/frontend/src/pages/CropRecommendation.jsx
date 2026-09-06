import { useState } from 'react'
import Card from '../components/Card'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { cropApi } from '../api/services'
import { getProfile } from '../utils/farmerProfile'
import { useTranslation } from '../context/LanguageContext'

const FIELDS = [
  { key: 'nitrogen', label: 'Nitrogen (N, kg/ha)', placeholder: 'e.g. 90' },
  { key: 'phosphorus', label: 'Phosphorus (P, kg/ha)', placeholder: 'e.g. 45' },
  { key: 'potassium', label: 'Potassium (K, kg/ha)', placeholder: 'e.g. 45' },
  { key: 'temperature', label: 'Temperature (°C)', placeholder: 'e.g. 26' },
  { key: 'humidity', label: 'Humidity (%)', placeholder: 'e.g. 70' },
  { key: 'rainfall', label: 'Rainfall (mm)', placeholder: 'e.g. 180' },
  { key: 'ph', label: 'Soil pH', placeholder: 'e.g. 6.5' },
]

export default function CropRecommendation() {
  const { t } = useTranslation()
  const [form, setForm] = useState({})
  const [location, setLocation] = useState(() => {
    const p = getProfile()
    return p.village || p.district || ''
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    const missing = FIELDS.filter((f) => form[f.key] === undefined || form[f.key] === '')
    if (missing.length) {
      setError(`Please fill in: ${missing.map((f) => f.label).join(', ')}`)
      return
    }
    setError(null)
    setLoading(true)
    try {
      const payload = Object.fromEntries(FIELDS.map((f) => [f.key, parseFloat(form[f.key])]))
      payload.location = location || undefined
      payload.has_soil_test = true
      const res = await cropApi.recommend(payload)
      setResult(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-foliage-900">{t('crop.title')}</h1>
        <p className="text-ink/70 mt-1">Enter your soil and climate values for suitable crop suggestions.</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 gap-4">
          {FIELDS.map((f) => (
            <div key={f.key}>
              <label className="block text-sm font-medium text-ink mb-1">{f.label}</label>
              <input
                type="number" step="any" placeholder={f.placeholder}
                value={form[f.key] ?? ''}
                onChange={(e) => handleChange(f.key, e.target.value)}
                className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none"
              />
            </div>
          ))}
          <div className="sm:col-span-2">
            <label className="block text-sm font-medium text-ink mb-1">Location (optional)</label>
            <input
              value={location} onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Sonipat, Haryana"
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none"
            />
          </div>
          {error && <div className="sm:col-span-2"><ErrorBanner message={error} /></div>}
          <div className="sm:col-span-2">
            <button
              type="submit" disabled={loading}
              className="bg-foliage-800 text-white rounded-xs px-6 py-2.5 text-sm font-medium hover:bg-foliage-900 disabled:opacity-60"
            >
              {loading ? 'Analyzing…' : 'Get Recommendations'}
            </button>
          </div>
        </form>
      </Card>

      {loading && <LoadingSpinner />}

      {result && (
        <div className="space-y-3">
          <h2 className="font-display text-lg text-foliage-900">Results</h2>
          <p className="text-xs text-ink/50">Model: {result.model_used}</p>
          {result.results.map((r) => (
            <Card key={r.crop} accent="wheat">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-display text-lg text-foliage-900">{r.crop}</h3>
                <span className="text-sm font-medium text-wheat-700">{r.suitability_score}% match</span>
              </div>
              <div className="w-full bg-foliage-50 rounded-full h-1.5 mb-2">
                <div className="bg-wheat-500 h-1.5 rounded-full" style={{ width: `${r.suitability_score}%` }} />
              </div>
              <p className="text-sm text-ink/70">{r.explanation}</p>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
