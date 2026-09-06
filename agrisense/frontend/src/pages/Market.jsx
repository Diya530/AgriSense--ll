import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Search, Info, TrendingUp, TrendingDown, Minus, MessageCircle } from 'lucide-react'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { marketApi } from '../api/services'
import { useTranslation } from '../context/LanguageContext'

const TREND_META = {
  up: { label: 'Up', icon: TrendingUp, className: 'bg-foliage-50 text-foliage-700' },
  down: { label: 'Down', icon: TrendingDown, className: 'bg-clay-400/10 text-clay-400' },
  stable: { label: 'Stable', icon: Minus, className: 'bg-wheat-100 text-wheat-700' },
}

function StatCard({ value, label, accent }) {
  return (
    <div className="bg-white border border-foliage-100 rounded-xs px-6 py-5 text-center">
      <p className={`text-3xl font-display ${accent}`}>{value}</p>
      <p className="text-sm text-ink/60 mt-1">{label}</p>
    </div>
  )
}

export default function Market() {
  const { t } = useTranslation()
  const [query, setQuery] = useState('')
  const [trendFilter, setTrendFilter] = useState('all')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const runSearch = async (q) => {
    setLoading(true)
    setError(null)
    try {
      const res = await marketApi.search(q)
      setResult(res.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { runSearch('') }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    runSearch(query.trim())
  }

  const visibleRows = useMemo(() => {
    if (!result) return []
    if (trendFilter === 'all') return result.results
    return result.results.filter((r) => r.trend === trendFilter)
  }, [result, trendFilter])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-foliage-900">{t('market.title')}</h1>
          <p className="text-ink/70 mt-1">
            Mandi prices & MSP comparison
            {result?.updated && ` · Updated: ${result.updated}`}
          </p>
        </div>
        <Link
          to="/chat"
          className="flex items-center gap-2 bg-foliage-800 text-white rounded-xs px-4 py-2.5 text-sm font-medium hover:bg-foliage-900"
        >
          <MessageCircle size={16} /> Ask Price Advice
        </Link>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorBanner message={error} />}

      {result && !loading && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard value={`${result.summary.rising} ↑`} label="Prices Rising" accent="text-foliage-700" />
            <StatCard value={`${result.summary.falling} ↓`} label="Prices Falling" accent="text-clay-400" />
            <StatCard value={`${result.summary.stable} →`} label="Stable Prices" accent="text-wheat-700" />
            <StatCard value={result.summary.commodities} label="Commodities" accent="text-foliage-900" />
          </div>

          <div className="bg-white border border-foliage-100 rounded-xs p-4 flex flex-wrap items-center gap-3">
            <form onSubmit={handleSubmit} className="flex flex-1 min-w-[240px] gap-2">
              <div className="relative flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/40" />
                <input
                  value={query} onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search crop, market, or state…"
                  className="w-full border border-foliage-100 rounded-xs pl-9 pr-3 py-2 text-sm focus:border-foliage-700 outline-none"
                />
              </div>
              <button type="submit" className="bg-foliage-800 text-white rounded-xs px-4 py-2 text-sm hover:bg-foliage-900">
                {t('common.search')}
              </button>
            </form>
            <select
              value={trendFilter} onChange={(e) => setTrendFilter(e.target.value)}
              className="border border-foliage-100 rounded-xs px-3 py-2 text-sm bg-white"
            >
              <option value="all">All Trends</option>
              <option value="up">Rising</option>
              <option value="down">Falling</option>
              <option value="stable">Stable</option>
            </select>
            <p className="flex items-center gap-1.5 text-xs text-ink/50">
              <Info size={13} /> Prices are indicative. Verify at your local mandi before selling.
            </p>
          </div>

          {/* {result.is_demo && (
            <div className="flex items-center gap-2 bg-wheat-100 border border-wheat-300 text-foliage-900 rounded-xs px-4 py-2.5 text-sm">
              <Info size={16} className="text-wheat-700 shrink-0" />
              Demo / Sample Data — not live prices. {result.message?.includes('DATA_GOV_IN') ? '' : result.message}
            </div>
          )} */}
          {!result.is_demo && result.message && (
            <p className="text-xs text-ink/50">{result.message}</p>
          )}

          {visibleRows.length === 0 ? (
            <div className="bg-white border border-foliage-100 rounded-xs p-8 text-center text-sm text-ink/60">
              {result.message && result.results.length === 0 ? result.message : 'No entries match this filter.'}
            </div>
          ) : (
            <div className="bg-white border border-foliage-100 rounded-xs overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-foliage-100 text-left text-xs text-ink/50 uppercase tracking-wide">
                    <th className="px-5 py-3 font-medium">Crop & Variety</th>
                    <th className="px-5 py-3 font-medium">Market</th>
                    <th className="px-5 py-3 font-medium">State</th>
                    <th className="px-5 py-3 font-medium text-right">Min ₹</th>
                    <th className="px-5 py-3 font-medium text-right">Max ₹</th>
                    <th className="px-5 py-3 font-medium text-right">Modal ₹</th>
                    <th className="px-5 py-3 font-medium text-right">MSP ₹</th>
                    <th className="px-5 py-3 font-medium">Trend</th>
                    <th className="px-5 py-3 font-medium text-right">vs MSP</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleRows.map((r, i) => {
                    const trend = TREND_META[r.trend]
                    const TrendIcon = trend?.icon
                    return (
                      <tr key={i} className="border-b border-foliage-50 last:border-0 hover:bg-foliage-50/50">
                        <td className="px-5 py-3">
                          <p className="font-medium text-foliage-900">{r.crop}</p>
                          {r.variety && <p className="text-xs text-ink/50">{r.variety}</p>}
                        </td>
                        <td className="px-5 py-3 text-ink/80">{r.market}</td>
                        <td className="px-5 py-3 text-ink/60">{r.state || '—'}</td>
                        <td className="px-5 py-3 text-right text-ink/70">{r.min_price ?? '—'}</td>
                        <td className="px-5 py-3 text-right text-ink/70">{r.max_price ?? '—'}</td>
                        <td className="px-5 py-3 text-right font-medium text-foliage-800">{r.modal_price}</td>
                        <td className="px-5 py-3 text-right text-ink/70">{r.msp ?? '—'}</td>
                        <td className="px-5 py-3">
                          {trend ? (
                            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${trend.className}`}>
                              <TrendIcon size={12} /> {trend.label}
                            </span>
                          ) : <span className="text-ink/40 text-xs">—</span>}
                        </td>
                        <td className={`px-5 py-3 text-right font-medium ${
                          r.vs_msp == null ? 'text-ink/40' : r.vs_msp < 0 ? 'text-clay-400' : 'text-foliage-700'
                        }`}>
                          {r.vs_msp == null ? 'N/A' : (r.vs_msp > 0 ? `+${r.vs_msp}` : r.vs_msp)}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  )
}
