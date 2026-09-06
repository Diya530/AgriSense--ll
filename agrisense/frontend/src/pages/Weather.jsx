import { useState, useEffect } from 'react'
import { Search, Droplets, Wind, Sunrise, Sunset } from 'lucide-react'
import Card from '../components/Card'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { weatherApi } from '../api/services'
import { getProfile, hasLocation } from '../utils/farmerProfile'
import { useTranslation } from '../context/LanguageContext'

export default function Weather() {
  const { t } = useTranslation()
  const [profile] = useState(() => getProfile())
  const [query, setQuery] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async (locationName) => {
    setLoading(true)
    setError(null)
    try {
      const params = locationName
        ? { location_name: locationName, days: 7 }
        : { latitude: profile.latitude, longitude: profile.longitude, days: 7 }
      const res = await weatherApi.get(params)
      setData(res.data)
    } catch (err) {
      setError(err.message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (hasLocation(profile)) {
      load()
    } else {
      setLoading(false)
    }
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    if (query.trim()) load(query.trim())
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-foliage-900">{t('weather.title')}</h1>
        <p className="text-ink/70 mt-1">{t('weather.subtitle')}</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2 max-w-md">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search a city, district, or village…"
          className="flex-1 border border-foliage-100 rounded-xs px-4 py-2.5 text-sm bg-white focus:border-foliage-700 outline-none"
        />
        <button type="submit" className="bg-foliage-800 text-white rounded-xs px-4 hover:bg-foliage-900">
          <Search size={18} />
        </button>
      </form>
      {!query && (
        <p className="text-xs text-ink/50 -mt-4">
          Showing your saved farm location. Search above to check another place instead — it won't change your saved location.
        </p>
      )}

      {!hasLocation(profile) && !query && (
        <ErrorBanner message="No saved location yet. Set your location in Profile, or search a place above." />
      )}
      {loading && <LoadingSpinner label="Fetching live weather…" />}
      {error && <ErrorBanner message={error} onRetry={() => load(query || undefined)} />}

      {data && !loading && (
        <div className="space-y-6">
          <Card accent="sky">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-sm text-ink/60">{data.location_name}</p>
                <p className="font-display text-6xl text-foliage-900 mt-1">
                  {Math.round(data.current.temperature_c)}°C
                </p>
                <p className="text-ink/70 mt-1">{data.current.description} · Feels like {Math.round(data.current.feels_like_c)}°C</p>
              </div>
              <div className="text-sm space-y-1.5 text-ink/70">
                <p className="flex items-center gap-2"><Droplets size={15} /> Humidity: {data.current.humidity_pct}%</p>
                <p className="flex items-center gap-2"><Wind size={15} /> Wind: {data.current.wind_speed_ms} m/s</p>
                {data.current.sunrise && (
                  <p className="flex items-center gap-2"><Sunrise size={15} /> {new Date(data.current.sunrise).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                )}
                {data.current.sunset && (
                  <p className="flex items-center gap-2"><Sunset size={15} /> {new Date(data.current.sunset).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                )}
              </div>
            </div>
            <p className="text-xs text-ink/40 mt-3">
              Forecast reflects the nearest weather grid point, not an on-farm sensor reading.
            </p>
            {data.is_cached && (
              <p className="text-xs text-clay-400 mt-1">
                Showing cached data from {new Date(data.fetched_at).toLocaleString()} ({data.source}) — live fetch is currently unavailable.
              </p>
            )}
          </Card>

          <div>
            <h2 className="font-display text-lg text-foliage-900 mb-3">7-Day Outlook</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3">
              {data.forecast?.map((d) => (
                <div key={d.date} className="bg-white border border-foliage-100 rounded-xs p-3 text-center">
                  <p className="text-xs text-ink/60">{new Date(d.date).toLocaleDateString([], { weekday: 'short' })}</p>
                  <p className="text-sm font-medium text-foliage-900 mt-1">{d.temp_max}° / {d.temp_min}°</p>
                  <p className="text-xs text-sky-500 mt-1">{d.rain_probability_pct}% chance of rain</p>
                  <p className="text-xs text-ink/50 mt-1">{d.condition}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
