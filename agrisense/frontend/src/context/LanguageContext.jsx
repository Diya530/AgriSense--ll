import { createContext, useContext, useState, useCallback } from 'react'
import { getProfile } from '../utils/farmerProfile'
import { translate } from '../i18n/translations'

const LanguageContext = createContext(null)

export function LanguageProvider({ children }) {
  // Read synchronously from localStorage — no backend round-trip needed
  // since the profile lives entirely in the browser.
  const [language, setLanguageState] = useState(() => getProfile().preferred_language || 'en')

  const setLanguage = useCallback((lang) => setLanguageState(lang), [])
  const t = useCallback((key) => translate(language, key), [language])

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, loaded: true }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useTranslation() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useTranslation must be used within LanguageProvider')
  return ctx
}
