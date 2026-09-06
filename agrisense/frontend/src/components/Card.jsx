const ACCENTS = {
  foliage: 'border-l-foliage-700',
  wheat: 'border-l-wheat-500',
  soil: 'border-l-soil-500',
  sky: 'border-l-sky-500',
  clay: 'border-l-clay-400',
}

export default function Card({ title, accent = 'foliage', children, className = '', icon: Icon }) {
  return (
    <div
      className={`bg-white rounded-xs shadow-soft border border-foliage-100 border-l-4 ${ACCENTS[accent]} p-5 ${className}`}
    >
      {title && (
        <div className="flex items-center gap-2 mb-3">
          {Icon && <Icon size={18} className="text-foliage-700" strokeWidth={1.75} />}
          <h3 className="font-display text-lg text-foliage-900">{title}</h3>
        </div>
      )}
      {children}
    </div>
  )
}
