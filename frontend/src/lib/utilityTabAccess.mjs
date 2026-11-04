// A bearer grant belongs only to this tab's sessionStorage. Never persist an
// account number/token in localStorage, a cookie, a URL or rendered markup.
export const TAB_TOKEN_KEY = 'moconix_library_tab_token'
export const TAB_TOKEN_HEADER = 'X-Moconix-Library-Token'
const tokenPattern = /^[A-Za-z0-9_-]{43}$/
const storageMessage = '이 탭의 저장소를 사용할 수 없습니다. 브라우저 설정을 확인한 뒤 다시 로그인해 주세요.'
const requestMessage = '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.'
const networkMessage = '네트워크 연결을 확인하고 다시 시도해 주세요.'
const downloadMessage = '다운로드하지 못했습니다. 잠시 후 다시 시도해 주세요.'
const loginMessage = '로그인 정보를 확인하지 못했습니다. 다시 로그인해 주세요.'
const authorizationMessage = '홈 화면에서 등록된 계좌번호로 다시 로그인해 주세요.'

function failure(message, status, code) {
  const error = new Error(message)
  if (status) error.status = status
  if (code) error.code = code
  return error
}

function attachmentName(disposition, fallback) {
  const encoded = disposition?.match(/filename\*\s*=\s*UTF-8''([^;]+)/i)
  const plain = disposition?.match(/filename\s*=\s*(?:"([^"]*)"|([^;]+))/i)
  let name
  if (encoded) {
    try { name = decodeURIComponent(encoded[1].trim()) } catch { /* Use the plain filename if present. */ }
  }
  name = name || plain?.[1] || plain?.[2]?.trim() || fallback
  name = String(name || '').replace(/\\/g, '/').split('/').pop().replace(/[<>:"|?*]/g, '')
  name = [...name].filter(character => character.charCodeAt(0) > 31).join('')
  if (!name || !/\.ex5$/i.test(name)) throw failure(downloadMessage)
  return name
}

function saveBrowserFile(blob, filename) {
  if (typeof document === 'undefined') throw failure(downloadMessage)
  const objectUrl = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  link.hidden = true
  document.body.appendChild(link)
  try { link.click() } finally {
    link.remove()
    // Allow the browser to begin consuming the object URL before releasing it.
    setTimeout(() => URL.revokeObjectURL(objectUrl), 1000)
  }
}

export function createUtilityAccessClient(environment = {}) {
  const getStorage = environment.getStorage || (() => typeof window === 'undefined' ? null : window.sessionStorage)
  const getCookie = environment.getCookie || (() => typeof document === 'undefined' ? '' : document.cookie)
  const getOrigin = environment.getOrigin || (() => typeof window === 'undefined' ? null : window.location.origin)
  const fetcher = environment.fetch || ((...args) => fetch(...args))
  const saveFile = environment.saveFile || saveBrowserFile
  let loginGeneration = 0

  function storage() {
    try { return getStorage() } catch { throw failure(storageMessage, null, 'storage') }
  }

  function readToken() {
    try {
      const target = storage()
      if (!target) return null
      const token = target.getItem(TAB_TOKEN_KEY)
      if (token && (typeof token !== 'string' || !tokenPattern.test(token))) { target.removeItem(TAB_TOKEN_KEY); return null }
      return token || null
    } catch { throw failure(storageMessage, null, 'storage') }
  }

  function discardToken(expected) {
    try {
      const target = storage()
      // A late response for an older grant must not erase a newer login.
      if (target && target.getItem(TAB_TOKEN_KEY) === expected) target.removeItem(TAB_TOKEN_KEY)
    } catch { /* A denied grant stays unusable even if browser storage is blocked. */ }
  }

  function csrfToken() {
    const token = getCookie().split(';').map(value => value.trim()).find(value => value.startsWith('csrftoken='))
    try { return token ? decodeURIComponent(token.slice('csrftoken='.length)) : '' } catch { return '' }
  }

  async function issueRequest(url, options, token, download = false) {
    const headers = new Headers(options.headers || {})
    headers.delete(TAB_TOKEN_HEADER)
    if (token) headers.set(TAB_TOKEN_HEADER, token)
    try {
      return await fetcher(url, { ...options, headers, credentials: 'same-origin', cache: 'no-store', redirect: 'error', mode: 'same-origin' })
    } catch { throw failure(download ? downloadMessage : networkMessage) }
  }

  async function revokeUnsavedToken(token) {
    try {
      await issueRequest('/api/utilities/logout/', { method: 'POST', headers: { 'X-CSRFToken': csrfToken() } }, token)
    } catch { /* Best effort: a token that could not be saved never authorizes this tab. */ }
    discardToken(token)
  }

  async function request(path, options = {}) {
    if (!['session', 'login', 'logout', 'library'].includes(path)) throw failure(requestMessage)
    const attempt = path === 'login' ? ++loginGeneration : null
    if (path === 'logout') loginGeneration += 1
    const usedToken = readToken()
    const response = await issueRequest(`/api/utilities/${path}/`, options, usedToken)
    const parsed = await response.json().catch(() => ({}))
    const body = parsed && typeof parsed === 'object' ? parsed : {}
    if (!response.ok) {
      if (response.status === 401 || path === 'login') discardToken(usedToken)
      throw failure(body.detail || requestMessage, response.status)
    }
    if (path === 'login') {
      const issuedToken = body.tab_token
      if (body.authenticated !== true || typeof issuedToken !== 'string' || !tokenPattern.test(issuedToken)) {
        discardToken(usedToken)
        throw failure(loginMessage)
      }
      if (attempt !== loginGeneration) {
        await revokeUnsavedToken(issuedToken)
        throw failure(loginMessage, null, 'superseded')
      }
      try {
        const target = storage()
        if (!target) throw failure(storageMessage, null, 'storage')
        target.setItem(TAB_TOKEN_KEY, issuedToken)
        if (target.getItem(TAB_TOKEN_KEY) !== issuedToken) throw failure(storageMessage, null, 'storage')
      } catch {
        await revokeUnsavedToken(issuedToken)
        discardToken(usedToken)
        throw failure(storageMessage, null, 'storage')
      }
      // Keep the bearer out of component state and any future rendered content.
      return { authenticated: true }
    }
    if ((path === 'session' && body.authenticated === false) || path === 'logout') discardToken(usedToken)
    return body
  }

  async function download(url, fallbackFilename) {
    const origin = getOrigin()
    let target
    try { target = new URL(url, origin || undefined) } catch { throw failure(downloadMessage) }
    if (!origin || target.origin !== origin || target.username || target.password || target.search || target.hash ||
        !/^\/api\/utilities\/download\/[A-Za-z0-9_-]{1,128}\/$/.test(target.pathname)) throw failure(downloadMessage)
    const usedToken = readToken()
    if (!usedToken) throw failure(authorizationMessage, 401)
    const response = await issueRequest(target.pathname, { method: 'GET' }, usedToken, true)
    if (!response.ok) {
      if (response.status === 401) discardToken(usedToken)
      const parsed = await response.json().catch(() => ({}))
      const body = parsed && typeof parsed === 'object' ? parsed : {}
      throw failure(body.detail || downloadMessage, response.status)
    }
    if (response.headers.get('Content-Type')?.split(';')[0].trim() !== 'application/octet-stream') throw failure(downloadMessage)
    const filename = attachmentName(response.headers.get('Content-Disposition'), fallbackFilename)
    let blob
    try { blob = await response.blob() } catch { throw failure(downloadMessage) }
    await saveFile(blob, filename)
    return { filename }
  }

  return { csrfToken, request, download, readToken }
}
