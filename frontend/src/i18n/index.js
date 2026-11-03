import { reactive } from 'vue'
import { normalizeLocale, translate } from './messages.mjs'

const preferenceKey = 'moconix_language'
function readPreference() {
  if (typeof window === 'undefined') return 'ko'
  try { const saved = window.localStorage.getItem(preferenceKey); if (saved) return normalizeLocale(saved) } catch { /* Cookie fallback for restricted storage. */ }
  const cookie = document.cookie.split('; ').find(row => row.startsWith(`${preferenceKey}=`))
  return normalizeLocale(cookie ? cookie.slice(preferenceKey.length + 1) : 'ko')
}
export const languageState = reactive({ locale: readPreference() })
export const t = (message, params) => translate(message, languageState.locale, params)
function updatePageLanguage() {
  if (typeof document === 'undefined') return
  document.documentElement.lang = languageState.locale
  document.title = t('MOCONIX | MT5 EA·인디케이터 맞춤 개발')
  const description = document.querySelector('meta[name="description"]')
  if (description) description.setAttribute('content', t('MT5 EA·인디케이터와 TradingView 지표를 맞춤 개발합니다. 매매 전략과 필요한 기능을 구현하고, 기존 프로그램의 수정 및 개선도 지원합니다.'))
  const websiteData = document.getElementById('moconix-website-data')
  if (websiteData) {
    try {
      const website = JSON.parse(websiteData.textContent)
      website.inLanguage = languageState.locale
      websiteData.textContent = JSON.stringify(website).replace(/</g, '\\u003c')
    } catch { /* Preserve unrelated page behavior if metadata was changed externally. */ }
  }
}
export function setLanguage(value) {
  languageState.locale = normalizeLocale(value)
  updatePageLanguage()
  if (typeof window === 'undefined') return
  try { window.localStorage.setItem(preferenceKey, languageState.locale) } catch { /* Preference is also stored in a non-sensitive cookie. */ }
  document.cookie = `${preferenceKey}=${languageState.locale}; Path=/; Max-Age=31536000; SameSite=Lax${window.location.protocol === 'https:' ? '; Secure' : ''}`
}
export function installLanguage(app) {
  updatePageLanguage()
  app.config.globalProperties.$t = t
  Object.defineProperty(app.config.globalProperties, '$locale', { get: () => languageState.locale })
}
