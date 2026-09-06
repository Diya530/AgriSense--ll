import { useState, useRef } from 'react'
import { Upload, ImageOff } from 'lucide-react'
import Card from '../components/Card'
import { useTranslation } from '../context/LanguageContext'
import { LoadingSpinner, ErrorBanner } from '../components/Feedback'
import { plantHealthApi } from '../api/services'

export default function PlantHealth() {
  const { t } = useTranslation()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const handleFile = (f) => {
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setError(null)
  }

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const res = await plantHealthApi.analyze(file)
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
        <h1 className="font-display text-3xl text-foliage-900">{t('plantHealth.title')}</h1>
        <p className="text-ink/70 mt-1">{t('plantHealth.subtitle')}</p>
      </div>

      <Card>
        <div
          onClick={() => inputRef.current?.click()}
          className="border-2 border-dashed border-foliage-300 rounded-xs p-8 text-center cursor-pointer hover:bg-foliage-50 transition-colors"
        >
          {preview ? (
            <img src={preview} alt="Selected crop" className="max-h-64 mx-auto rounded-xs" />
          ) : (
            <div className="text-foliage-700">
              <Upload size={32} className="mx-auto mb-2" />
              <p className="text-sm font-medium">Click to upload a photo</p>
              <p className="text-xs text-ink/50 mt-1">JPEG, PNG or WebP, up to 8MB</p>
            </div>
          )}
          <input
            ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </div>
        {file && (
          <button
            onClick={handleSubmit} disabled={loading}
            className="mt-4 bg-foliage-800 text-white rounded-xs px-6 py-2.5 text-sm font-medium hover:bg-foliage-900 disabled:opacity-60"
          >
            {loading ? 'Analyzing…' : 'Analyze Photo'}
          </button>
        )}
      </Card>

      {loading && <LoadingSpinner label="Analyzing your photo…" />}
      {error && <ErrorBanner message={error} onRetry={handleSubmit} />}

      {result && (
        <Card accent={result.low_confidence ? 'clay' : 'foliage'}>
          {result.diagnosis ? (
            <>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-display text-xl text-foliage-900">{result.diagnosis}</h3>
                {result.confidence != null && (
                  <span className="text-sm text-ink/60">{Math.round(result.confidence * 100)}% confidence</span>
                )}
              </div>
              {result.crop_guess && <p className="text-sm text-ink/60 mb-3">Likely crop: {result.crop_guess}</p>}
              {result.symptoms?.length > 0 && (
                <div className="mb-3">
                  <p className="text-sm font-medium text-ink mb-1">Symptoms observed</p>
                  <ul className="text-sm text-ink/70 space-y-0.5">
                    {result.symptoms.map((s, i) => <li key={i}>• {s}</li>)}
                  </ul>
                </div>
              )}
              {result.recommended_action && (
                <div className="mb-3">
                  <p className="text-sm font-medium text-ink mb-1">Recommended action</p>
                  <p className="text-sm text-ink/70">{result.recommended_action}</p>
                </div>
              )}
              {result.prevention && (
                <div>
                  <p className="text-sm font-medium text-ink mb-1">Prevention</p>
                  <p className="text-sm text-ink/70">{result.prevention}</p>
                </div>
              )}
            </>
          ) : (
            <div className="flex gap-3">
              <ImageOff size={20} className="text-clay-400 shrink-0 mt-0.5" />
              <p className="text-sm text-ink/80">
                We couldn't confidently diagnose this photo. {result.recommended_action}
              </p>
            </div>
          )}
          {result.note && (
            <p className="text-xs text-clay-400 mt-3 pt-3 border-t border-foliage-100">{result.note}</p>
          )}
        </Card>
      )}
    </div>
  )
}
