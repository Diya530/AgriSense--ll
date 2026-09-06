import { AlertTriangle, Loader2 } from 'lucide-react'

export function LoadingSpinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center gap-2 text-foliage-700 py-6 justify-center">
      <Loader2 size={20} className="animate-spin" />
      <span className="font-sans text-sm">{label}</span>
    </div>
  )
}

export function ErrorBanner({ message, onRetry }) {
  if (!message) return null
  return (
    <div className="flex items-start gap-3 bg-clay-400/10 border border-clay-400/40 text-ink rounded-xs p-4">
      <AlertTriangle size={20} className="text-clay-400 shrink-0 mt-0.5" />
      <div className="flex-1 text-sm">
        <p>{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-sm font-medium text-foliage-800 underline underline-offset-2 hover:text-foliage-900"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  )
}
