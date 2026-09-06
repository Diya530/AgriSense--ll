import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, MessageCircle, CloudSun, Sprout, FlaskConical,
  Leaf, Droplets, TrendingUp, User, Settings, Menu,
} from 'lucide-react'
import { useState } from 'react'
import Logo from './Logo'
import { useTranslation } from '../context/LanguageContext'

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { t } = useTranslation()

  const NAV_ITEMS = [
    { to: '/dashboard', label: t('nav.dashboard'), icon: LayoutDashboard },
    { to: '/chat', label: t('nav.chat'), icon: MessageCircle },
    { to: '/weather', label: t('nav.weather'), icon: CloudSun },
    { to: '/crop-recommendation', label: t('nav.crop'), icon: Sprout },
    { to: '/soil-analysis', label: t('nav.soil'), icon: FlaskConical },
    { to: '/plant-health', label: t('nav.plantHealth'), icon: Leaf },
    { to: '/irrigation', label: t('nav.irrigation'), icon: Droplets },
    { to: '/market', label: t('nav.market'), icon: TrendingUp },
    { to: '/profile', label: t('nav.profile'), icon: User },
    { to: '/settings', label: t('nav.settings'), icon: Settings },
  ]

  const SidebarContent = (
    <>
      <div className="px-5 py-6">
        <Logo size={30} />
      </div>
      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xs text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-foliage-800 text-white'
                  : 'text-foliage-900 hover:bg-foliage-50'
              }`
            }
          >
            <Icon size={18} strokeWidth={1.75} />
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  )

  return (
    <div className="min-h-screen flex bg-canvas">
      <aside className="hidden md:flex md:flex-col w-64 bg-white border-r border-foliage-100 fixed inset-y-0">
        {SidebarContent}
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-ink/40" onClick={() => setMobileOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 bg-white flex flex-col">
            {SidebarContent}
          </aside>
        </div>
      )}

      <div className="flex-1 md:ml-64 flex flex-col min-h-screen">
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-foliage-100 sticky top-0 z-30">
          <Logo size={26} />
          <button onClick={() => setMobileOpen(true)} aria-label="Open menu">
            <Menu size={24} className="text-foliage-800" />
          </button>
        </header>
        <main className="flex-1 p-4 md:p-8 max-w-6xl w-full mx-auto">{children}</main>
      </div>
    </div>
  )
}
