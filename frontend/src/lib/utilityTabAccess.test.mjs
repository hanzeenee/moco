import test from 'node:test'
import assert from 'node:assert/strict'
import { createUtilityAccessClient, TAB_TOKEN_HEADER, TAB_TOKEN_KEY } from './utilityTabAccess.mjs'

const A = 'A'.repeat(43)
const B = 'B'.repeat(43)
const URL = '/api/utilities/download/auth-bridge/'

function storage(initial = null) {
  const data = new Map(initial ? [[TAB_TOKEN_KEY, initial]] : [])
  return {
    data,
    getItem: key => data.get(key) ?? null,
    setItem: (key, value) => data.set(key, String(value)),
    removeItem: key => data.delete(key),
    clear: () => data.clear(),
  }
}
const json = (value, status = 200) => new Response(JSON.stringify(value), { status, headers: { 'Content-Type': 'application/json' } })
const binary = (disposition = 'attachment; filename="MOCONIX_AuthBridge.ex5"') => new Response('ex5-fixture', {
  headers: { 'Content-Type': 'application/octet-stream', 'Content-Disposition': disposition },
})
function client(target, fetch, saveFile = () => {}) {
  return createUtilityAccessClient({ getStorage: () => target, fetch, getOrigin: () => 'https://moconix.com', getCookie: () => 'moconix_language=ko; csrftoken=csrf-test', saveFile })
}

test('a successful login saves only the token in its own tab; refresh/home reuse it and a fresh tab cannot', async () => {
  const first = storage(), second = storage(), fresh = storage()
  let issued = 0
  const fetcher = async (url, options) => {
    if (url.endsWith('/login/')) return json({ authenticated: true, tab_token: issued++ === 0 ? A : B })
    assert.equal(url, '/api/utilities/session/')
    return json({ authenticated: [A, B].includes(options.headers.get(TAB_TOKEN_HEADER)) })
  }
  const one = client(first, fetcher), two = client(second, fetcher)
  const result = await one.request('login', { method: 'POST', body: JSON.stringify({ account_number: '77112233' }) })
  assert.deepEqual(result, { authenticated: true })
  assert.deepEqual([...first.data], [[TAB_TOKEN_KEY, A]])
  assert.equal(second.data.size, 0)
  await two.request('login', { method: 'POST' })
  assert.equal(first.getItem(TAB_TOKEN_KEY), A)
  assert.equal(second.getItem(TAB_TOKEN_KEY), B)
  assert.equal((await client(first, fetcher).request('session')).authenticated, true)
  assert.equal((await client(fresh, fetcher).request('session')).authenticated, false)
  first.clear() // A closed tab discards sessionStorage; it does not affect another tab.
  assert.equal((await one.request('session')).authenticated, false)
  assert.equal((await two.request('session')).authenticated, true)
})

test('all utility requests use the stored header and fixed same-origin/no-store/no-redirect options', async () => {
  const target = storage(A)
  const access = client(target, async (url, options) => {
    assert.equal(url, '/api/utilities/library/')
    assert.equal(options.headers.get(TAB_TOKEN_HEADER), A)
    assert.equal(options.headers.get('X-CSRFToken'), 'csrf')
    assert.equal(options.credentials, 'same-origin')
    assert.equal(options.mode, 'same-origin')
    assert.equal(options.redirect, 'error')
    assert.equal(options.cache, 'no-store')
    assert.ok(!url.includes(A))
    return json({ items: [] })
  })
  await access.request('library', { headers: { [TAB_TOKEN_HEADER]: 'forged', 'X-CSRFToken': 'csrf' }, credentials: 'include', mode: 'cors', redirect: 'follow' })
})

test('missing or malformed stored tokens never fall back to a caller header, cookie or another storage key', async () => {
  const target = storage('invalid')
  const access = client(target, async (_, options) => {
    assert.equal(options.headers.get(TAB_TOKEN_HEADER), null)
    return json({ authenticated: false })
  })
  await access.request('session', { headers: { [TAB_TOKEN_HEADER]: A } })
  assert.equal(target.data.size, 0)
  await assert.rejects(access.request('https://evil.invalid'), /요청을 처리하지 못했습니다/)
})

test('401 and unauthenticated session replies clear the current tab grant', async () => {
  for (const path of ['library', 'session']) {
    const target = storage(A)
    const access = client(target, async () => path === 'library' ? json({ detail: '자료실 로그인이 필요합니다.' }, 401) : json({ authenticated: false }))
    if (path === 'library') await assert.rejects(access.request(path), error => error.status === 401)
    else assert.equal((await access.request(path)).authenticated, false)
    assert.equal(target.getItem(TAB_TOKEN_KEY), null)
  }
})

test('late 401 or session-false replies cannot erase a newer successful login', async () => {
  for (const path of ['library', 'session']) {
    const target = storage(A)
    let finish
    const pending = new Promise(resolve => { finish = resolve })
    const access = client(target, () => pending)
    const result = access.request(path)
    target.setItem(TAB_TOKEN_KEY, B)
    finish(path === 'library' ? json({ detail: '자료실 로그인이 필요합니다.' }, 401) : json({ authenticated: false }))
    if (path === 'library') await assert.rejects(result, error => error.status === 401)
    else await result
    assert.equal(target.getItem(TAB_TOKEN_KEY), B)
  }
})

test('invalid relogin clears the revoked old token while a resource error leaves a valid grant intact', async () => {
  const target = storage(A)
  const access = client(target, async () => json({ detail: '등록되지 않았거나 이용이 중지된 계좌번호입니다.' }, 403))
  await assert.rejects(access.request('login', { method: 'POST' }), error => error.status === 403)
  assert.equal(target.getItem(TAB_TOKEN_KEY), null)
  target.setItem(TAB_TOKEN_KEY, B)
  const missing = client(target, async () => json({}, 404))
  await assert.rejects(missing.download(URL, 'helper.ex5'), error => error.status === 404)
  assert.equal(target.getItem(TAB_TOKEN_KEY), B)
})

test('storage read failure fails closed before any authenticated request', async () => {
  let calls = 0
  const access = createUtilityAccessClient({ getStorage: () => { throw new Error('blocked') }, fetch: () => { calls++ } })
  await assert.rejects(access.request('library'), error => error.code === 'storage')
  assert.equal(calls, 0)
})

test('failed or unverifiable token saves revoke the newly issued grant and never report login success', async () => {
  for (const mode of ['throw', 'no-op']) {
    const target = storage()
    target.setItem = () => { if (mode === 'throw') throw new Error('QuotaExceededError') }
    const calls = []
    const access = client(target, async (url, options) => {
      calls.push({ url, options })
      return url.endsWith('/login/') ? json({ authenticated: true, tab_token: A }) : json({ authenticated: false })
    })
    await assert.rejects(access.request('login', { method: 'POST' }), error => error.code === 'storage')
    assert.equal(calls.length, 2)
    assert.equal(calls[1].url, '/api/utilities/logout/')
    assert.equal(calls[1].options.method, 'POST')
    assert.equal(calls[1].options.headers.get(TAB_TOKEN_HEADER), A)
    assert.equal(calls[1].options.headers.get('X-CSRFToken'), 'csrf-test')
    assert.equal(target.data.size, 0)
  }
})

test('SSR imports and CSRF lookup are safe without browser globals; malformed login grants are refused', async () => {
  const server = createUtilityAccessClient()
  assert.equal(server.readToken(), null)
  assert.equal(server.csrfToken(), '')
  const access = client(storage(), async () => json({ authenticated: true, tab_token: 'bad' }))
  await assert.rejects(access.request('login', { method: 'POST' }), /로그인 정보를 확인하지 못했습니다/)
})

test('EX5 downloads send the tab header and preserve attachment filename and binary contents', async () => {
  const saved = []
  const target = storage(A)
  const access = client(target, async (url, options) => {
    assert.equal(url, URL)
    assert.equal(options.headers.get(TAB_TOKEN_HEADER), A)
    assert.equal(options.redirect, 'error')
    assert.equal(options.mode, 'same-origin')
    assert.equal(options.cache, 'no-store')
    return binary("attachment; filename*=UTF-8''%EC%9D%B8%EC%A6%9DEA.ex5")
  }, async (blob, filename) => saved.push({ filename, contents: await blob.text() }))
  const result = await access.download(URL, 'fallback.ex5')
  assert.deepEqual(result, { filename: '인증EA.ex5' })
  assert.deepEqual(saved, [{ filename: '인증EA.ex5', contents: 'ex5-fixture' }])
  assert.equal(target.getItem(TAB_TOKEN_KEY), A)
})

test('download URL validation prevents bearer delivery to another origin, a query, fragment or nonresource path', async () => {
  let calls = 0
  const access = client(storage(A), async () => { calls++; return binary() })
  for (const url of ['https://evil.invalid/api/utilities/download/a/', '//evil.invalid/api/utilities/download/a/',
    URL + '?token=secret', URL + '#token', '/media/file.ex5', 'https://name:password@moconix.com' + URL]) {
    await assert.rejects(access.download(url, 'file.ex5'), /다운로드하지 못했습니다/)
  }
  assert.equal(calls, 0)
})

test('missing tokens, denied downloads, HTML/JSON and non-EX5 attachments are never saved as EX5', async () => {
  let saved = 0
  const noToken = client(storage(), async () => { throw new Error('must not fetch') }, () => { saved++ })
  await assert.rejects(noToken.download(URL, 'helper.ex5'), error => error.status === 401)
  for (const response of [json({ detail: '자료실 로그인이 필요합니다.' }, 401), json({ authenticated: false }),
    new Response('<h1>Unavailable</h1>', { headers: { 'Content-Type': 'text/html' } }), binary('attachment; filename="source.mq5"')]) {
    const target = storage(A)
    const access = client(target, async () => response, () => { saved++ })
    await assert.rejects(access.download(URL, 'helper.ex5'))
    if (response.status === 401) assert.equal(target.getItem(TAB_TOKEN_KEY), null)
  }
  assert.equal(saved, 0)
})

test('an old download denial cannot clear a new login, and logout clears only its own tab', async () => {
  const target = storage(A), other = storage(B)
  let finish
  const pending = new Promise(resolve => { finish = resolve })
  const access = client(target, () => pending)
  const download = access.download(URL, 'helper.ex5')
  target.setItem(TAB_TOKEN_KEY, B)
  finish(json({ detail: '자료실 로그인이 필요합니다.' }, 401))
  await assert.rejects(download, error => error.status === 401)
  assert.equal(target.getItem(TAB_TOKEN_KEY), B)
  await client(target, async () => json({ authenticated: false })).request('logout', { method: 'POST' })
  assert.equal(target.getItem(TAB_TOKEN_KEY), null)
  assert.equal(other.getItem(TAB_TOKEN_KEY), B)
})

test('a superseded successful login is revoked and rejected before it can replace a newer login or navigate', async () => {
  const target = storage(A)
  const issuedEarlier = 'C'.repeat(43)
  let finishFirst, finishSecond, logins = 0, navigations = 0
  const revoked = []
  const access = client(target, (url, options) => {
    if (url.endsWith('/logout/')) { revoked.push(options.headers.get(TAB_TOKEN_HEADER)); return Promise.resolve(json({ authenticated: false })) }
    logins++
    return new Promise(resolve => { if (logins === 1) finishFirst = resolve; else finishSecond = resolve })
  })
  const earlier = access.request('login', { method: 'POST' }).then(result => { navigations++; return result })
  const later = access.request('login', { method: 'POST' }).then(result => { navigations++; return result })
  finishSecond(json({ authenticated: true, tab_token: B }))
  await later
  finishFirst(json({ authenticated: true, tab_token: issuedEarlier }))
  await assert.rejects(earlier, error => error.code === 'superseded')
  assert.equal(target.getItem(TAB_TOKEN_KEY), B)
  assert.deepEqual(revoked, [issuedEarlier])
  assert.equal(navigations, 1)
})

test('an older failed relogin cannot clear a newer successful login', async () => {
  const target = storage(A)
  let finishFirst, finishSecond, logins = 0
  const access = client(target, () => new Promise(resolve => { if (++logins === 1) finishFirst = resolve; else finishSecond = resolve }))
  const earlier = access.request('login', { method: 'POST' })
  const later = access.request('login', { method: 'POST' })
  finishSecond(json({ authenticated: true, tab_token: B }))
  await later
  finishFirst(json({ detail: '등록되지 않았거나 이용이 중지된 계좌번호입니다.' }, 403))
  await assert.rejects(earlier, error => error.status === 403)
  assert.equal(target.getItem(TAB_TOKEN_KEY), B)
})
