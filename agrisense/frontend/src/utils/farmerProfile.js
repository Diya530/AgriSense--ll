// Farmer profile storage — localStorage only, no backend persistence.
// This is the single source of truth for "who is this farmer" on this
// browser/device. There is no login, no server-side profile, and no sync
// across devices — by design, per the stateless architecture (see README).

const STORAGE_KEY = 'agrisense_farmer_profile'

const DEFAULT_PROFILE = {
  name: '',
  preferred_language: 'en',
  village: '',
  district: '',
  state: '',
  latitude: null,
  longitude: null,
  land_area_acres: null,
  soil_type: '',
  irrigation_type: '',
  current_crop: '',
  farming_goals: '',
}

export function getProfile() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULT_PROFILE }
    return { ...DEFAULT_PROFILE, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULT_PROFILE }
  }
}

export function saveProfile(profile) {
  const merged = { ...getProfile(), ...profile }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
  return merged
}

export function hasLocation(profile) {
  return profile && profile.latitude != null && profile.longitude != null
}

export function isProfileComplete(profile) {
  return Boolean(profile?.current_crop && hasLocation(profile))
}
