import { useState } from 'react'
import Card from '../components/Card'
import { getProfile, saveProfile } from '../utils/farmerProfile'
import { useTranslation } from '../context/LanguageContext'

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)' },
  { code: 'bn', label: 'বাংলা (Bengali)' },
  { code: 'mr', label: 'मराठी (Marathi)' },
  { code: 'te', label: 'తెలుగు (Telugu)' },
  { code: 'ta', label: 'தமிழ் (Tamil)' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)' },
  { code: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { code: 'ml', label: 'മലയാളം (Malayalam)' },
  { code: 'or', label: 'ଓଡ଼ିଆ (Odia)' },
]

export default function Profile() {
  const { t, setLanguage } = useTranslation()
  const [form, setForm] = useState(() => getProfile())
  const [saved, setSaved] = useState(false)
  const [geoStatus, setGeoStatus] = useState(null)

  const set = (key, value) => { setForm((f) => ({ ...f, [key]: value })); setSaved(false) }

  const useGeolocation = () => {
    if (!navigator.geolocation) {
      setGeoStatus('Geolocation is not supported by your browser.')
      return
    }
    setGeoStatus('Locating…')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        set('latitude', pos.coords.latitude)
        set('longitude', pos.coords.longitude)
        setGeoStatus('Location captured. Save to keep it.')
      },
      () => setGeoStatus('Could not get your location — check browser permissions.'),
    )
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const numeric = {
      ...form,
      latitude: form.latitude === '' ? null : Number(form.latitude),
      longitude: form.longitude === '' ? null : Number(form.longitude),
      land_area_acres: form.land_area_acres === '' ? null : Number(form.land_area_acres),
    }
    const result = saveProfile(numeric)
    setForm(result)
    setLanguage(result.preferred_language || 'en')
    setSaved(true)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-foliage-900">{t('profile.title')}</h1>
        <p className="text-ink/70 mt-1">
          {t('profile.subtitle')} Saved only in this browser — no account, no server storage.
        </p>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Name" value={form.name} onChange={(v) => set('name', v)} />
            <Field label="Preferred language">
              <select value={form.preferred_language || 'en'} onChange={(e) => set('preferred_language', e.target.value)}
                className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm bg-white">
                {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
              </select>
            </Field>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <Field label="Village" value={form.village} onChange={(v) => set('village', v)} />
            <Field label="District" value={form.district} onChange={(v) => set('district', v)} />
            <Field label="State" value={form.state} onChange={(v) => set('state', v)} />
          </div>

          <div className="flex items-end gap-3">
            <Field label="Latitude" type="number" value={form.latitude} onChange={(v) => set('latitude', v)} />
            <Field label="Longitude" type="number" value={form.longitude} onChange={(v) => set('longitude', v)} />
            <button type="button" onClick={useGeolocation}
              className="text-sm text-foliage-800 underline underline-offset-2 mb-2.5 whitespace-nowrap">
              Use my location
            </button>
          </div>
          {geoStatus && <p className="text-xs text-ink/60">{geoStatus}</p>}

          <div className="grid sm:grid-cols-3 gap-4">
            <Field label="Land area (acres)" type="number" value={form.land_area_acres} onChange={(v) => set('land_area_acres', v)} />
            <Field label="Soil type" value={form.soil_type} onChange={(v) => set('soil_type', v)} />
            <Field label="Irrigation type" value={form.irrigation_type} onChange={(v) => set('irrigation_type', v)} />
          </div>

          <Field label="Current crop" value={form.current_crop} onChange={(v) => set('current_crop', v)} />

          <div>
            <label className="block text-sm font-medium text-ink mb-1">Farming goals</label>
            <textarea value={form.farming_goals || ''} onChange={(e) => set('farming_goals', e.target.value)} rows={3}
              className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none" />
          </div>

          {saved && <p className="text-sm text-foliage-700">Profile saved to this browser.</p>}

          <button type="submit"
            className="bg-foliage-800 text-white rounded-xs px-6 py-2.5 text-sm font-medium hover:bg-foliage-900">
            {t('common.save')}
          </button>
        </form>
      </Card>
    </div>
  )
}

function Field({ label, value, onChange, type = 'text', children }) {
  return (
    <div className="flex-1">
      <label className="block text-sm font-medium text-ink mb-1">{label}</label>
      {children || (
        <input
          type={type} value={value ?? ''} onChange={(e) => onChange(e.target.value)}
          className="w-full border border-foliage-100 rounded-xs px-3 py-2.5 text-sm focus:border-foliage-700 outline-none"
        />
      )}
    </div>
  )
}
