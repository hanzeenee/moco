import { reactive } from 'vue'
import { normalizeLocale, translate } from './messages.mjs'

const preferenceKey = 'moconix_language'
function readPreference() {
  try { const saved = window.localStorage.getItem(preferenceKey); if (saved) return normalizeLocale(saved) } catch { /* Cookie fallback for restricted storage. */ }
  const cookie = document.cookie.split('; ').find(row => row.startsWith(`${preferenceKey}=`))
  return normalizeLocale(cookie ? cookie.slice(preferenceKey.length + 1) : 'ko')
}
export const languageState = reactive({ locale: readPreference() })
export const t = (message, params) => translate(message, languageState.locale, params)
export function setLanguage(value) {
  languageState.locale = normalizeLocale(value)
  document.documentElement.lang = languageState.locale
  try { window.localStorage.setItem(preferenceKey, languageState.locale) } catch { /* Preference is also stored in a non-sensitive cookie. */ }
  document.cookie = `${preferenceKey}=${languageState.locale}; Path=/; Max-Age=31536000; SameSite=Lax${window.location.protocol === 'https:' ? '; Secure' : ''}`
}
export function installLanguage(app) {
  document.documentElement.lang = languageState.locale
  app.config.globalProperties.$t = t
  Object.defineProperty(app.config.globalProperties, '$locale', { get: () => languageState.locale })
}
