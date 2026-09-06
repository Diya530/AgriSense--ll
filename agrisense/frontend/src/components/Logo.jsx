/**
 * AgriSense wordmark: a leaf built from two organic curves with a small
 * circuit-node accent on the tip, suggesting "agriculture + intelligence"
 * without leaning on cliché neon/glow AI iconography.
 */
export default function Logo({ size = 32, showWordmark = true, className = '' }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg width={size} height={size} viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M20 34C20 34 8 28 8 15C8 15 16 9 24 13C24 13 30 17 30 24C30 30 25 33 20 34Z"
          fill="#2E5A2A"
        />
        <path
          d="M20 34C20 34 12 25 14 14C14 14 20 11 24 15C24 15 27 20 25 26C23 31 20 34 20 34Z"
          fill="#4C7A44"
        />
        <path d="M20 34V17" stroke="#EEF3EC" strokeWidth="1.4" strokeLinecap="round" />
        <circle cx="26" cy="12" r="3" fill="#D4A017" />
        <circle cx="26" cy="12" r="1" fill="#1F3D2B" />
      </svg>
      {showWordmark && (
        <span className="font-display text-2xl text-foliage-900 leading-none">AgriSense</span>
      )}
    </div>
  )
}
