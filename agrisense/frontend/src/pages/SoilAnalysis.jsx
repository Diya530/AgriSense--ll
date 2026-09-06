import { useState } from 'react'
import Card from '../components/Card'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { soilApi } from '../api/services'
import { getProfile } from '../utils/farmerProfile'
import { useTranslation } from '../context/LanguageContext'

const SOIL_TYPES = ['Alluvial', 'Black (Regur)', 'Red', 'Laterite', 'Sandy', 'Clay']
const FIELDS = [
  { key: 'nitrogen', label: 'Nitrogen (N)' },
  { key: 'phosphorus', label: 'Phosphorus (P)' },
  { key: 'potassium', label: 'Potassium (K)' },
  { key: 'ph', label: 'Soil pH' },
  { key: 'moisture', label: 'Moisture (%)' },
]

export default function SoilAnalysis() {
  const { t } = useTranslation()
  const [form, setForm] = useState({})
  const [soilType, setSoilType] = useState(() => getProfile().soil_type || '')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const payload = { soil_type: soilType || undefined }
      FIELDS.forEach((f) => {
        if (form[f.key] !== undefined && form[f.key] !== '') payload[f.key] = parseFloat(form[f.key])
      })
      const res = await soilApi.analyze(payload)
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
        <h1 className="font-display text-3xl text-foliage-900">{t('soil.title')}</h1>
        <p className="text-ink/70 mt-1">{t('soil.subtitle')}</p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-ink mb-1">Soil type</label>
            <select value={soilType} onChange={(e) => setSoilType(e.target.value)}
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm bg-white">
              <option value="">Not sure / skip</option>
              {SOIL_TYPES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          {FIELDS.map((f) => (
            <div key={f.key}>
              <label className="block text-sm font-medium text-ink mb-1">
                {f.label} <span className="text-ink/40 font-normal">({t('common.optional')})</span>
              </label>
              <input
                type="number" step="any" placeholder="Don't know? Leave blank"
                value={form[f.key] ?? ''}
                onChange={(e) => setForm((s) => ({ ...s, [f.key]: e.target.value }))}
                className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none"
              />
            </div>
          ))}
          {error && <div className="sm:col-span-2"><ErrorBanner message={error} /></div>}
          <div className="sm:col-span-2">
            <button
              type="submit" disabled={loading}
              className="bg-foliage-800 text-white rounded-xs px-6 py-2.5 text-sm font-medium hover:bg-foliage-900 disabled:opacity-60"
            >
              {loading ? 'Analyzing…' : 'Analyze Soil'}
            </button>
          </div>
        </form>
      </Card>

      {loading && <LoadingSpinner />}

      {result && (
        <div className="grid sm:grid-cols-2 gap-4">
          {result.used_generic_guidance && (
            <ErrorBanner message="No lab values were provided — this guidance is based on general soil-type characteristics, not your specific field. A soil test will give a more precise answer." />
          )}
          <Card title="pH Status" accent="soil">
            <p className="text-lg font-display text-foliage-900">{result.ph_status}</p>
          </Card>
          <Card title="Nutrient Levels" accent="foliage">
            <ul className="text-sm space-y-1">
              {Object.entries(result.nutrient_status).map(([k, v]) => (
                <li key={k} className="flex justify-between">
                  <span className="capitalize text-ink/70">{k}</span>
                  <span className={`font-medium ${v === 'Low' ? 'text-clay-400' : v === 'High' ? 'text-wheat-700' : v === 'Unknown' ? 'text-ink/40' : 'text-foliage-700'}`}>{v}</span>
                </li>
              ))}
            </ul>
          </Card>
          {result.suitable_crops.length > 0 && (
            <Card title="Suitable Crops" accent="wheat">
              <div className="flex flex-wrap gap-2">
                {result.suitable_crops.map((c) => (
                  <span key={c} className="bg-foliage-50 text-foliage-800 text-sm px-3 py-1 rounded-full">{c}</span>
                ))}
              </div>
            </Card>
          )}
          <Card title="Fertilizer Guidance" accent="clay">
            <ul className="text-sm space-y-1.5 text-ink/80">
              {result.fertilizer_guidance.map((g, i) => <li key={i}>• {g}</li>)}
            </ul>
          </Card>
          <Card title="Improvement Recommendations" accent="sky" className="sm:col-span-2">
            <ul className="text-sm space-y-1.5 text-ink/80">
              {result.improvement_recommendations.map((g, i) => <li key={i}>• {g}</li>)}
            </ul>
          </Card>
        </div>
      )}
    </div>
  )
}
