import test from 'node:test'
import assert from 'node:assert/strict'
import { libraryPage, libraryPageLinks } from './utilityLibrary.mjs'

const resources = (ea, indicator = 0) => [
  ...Array.from({ length: ea }, (_, index) => ({ id: `ea-${index}`, type: 'ea' })),
  ...Array.from({ length: indicator }, (_, index) => ({ id: `indicator-${index}`, type: 'indicator' })),
  { id: 'auth-bridge', type: 'helper' },
]

test('each category gets independent nine-item pages, without duplicated or skipped files', () => {
  for (const count of [0, 1, 8, 9, 10, 18, 19, 30, 100]) {
    const items = resources(count, count)
    for (const type of ['ea', 'indicator']) {
      const first = libraryPage(items, type)
      assert.equal(first.pageCount, Math.ceil(count / 9))
      const seen = []
      for (let page = 1; page <= first.pageCount; page += 1) {
        const result = libraryPage(items, type, page)
        assert.ok(result.items.length <= 9)
        assert.ok(result.items.every(item => item.type === type))
        seen.push(...result.items.map(item => item.id))
      }
      assert.equal(new Set(seen).size, count)
      assert.deepEqual(seen, items.filter(item => item.type === type).map(item => item.id))
    }
  }
})

test('empty and changed catalogs clamp pages and never expose helpers or an all category', () => {
  const items = resources(19, 1)
  assert.equal(libraryPage(items, 'ea', 999).page, 3)
  assert.equal(libraryPage(items, 'ea', -1).page, 1)
  assert.equal(libraryPage(items, 'indicator', 3).page, 1)
  assert.deepEqual(libraryPage([], 'ea', 3), { filteredItems: [], pageCount: 0, page: 1, items: [] })
  assert.equal(libraryPage(items, 'all').items.length, 0)
  assert.equal(libraryPage(items, 'helper').items.length, 0)
  assert.equal(libraryPage(items, 'ea', NaN).page, 1)
})

test('page navigation stays compact while retaining the first, current and last pages', () => {
  assert.deepEqual(libraryPageLinks(1, 0), [])
  assert.deepEqual(libraryPageLinks(1, 1), [1])
  assert.deepEqual(libraryPageLinks(1, 4), [1, 2, 3, 4])
  assert.deepEqual(libraryPageLinks(6, 12), [1, null, 5, 6, 7, null, 12])
  for (let page = 1; page <= 20; page += 1) {
    const links = libraryPageLinks(page, 20)
    assert.ok(links.includes(1) && links.includes(page) && links.includes(20))
    assert.ok(links.length <= 7)
  }
})


test('search matches titles and descriptions across both kinds without helpers', () => {
  const items = [
    { id: 'ea', type: 'ea', title: '양방향 돌파 EA', description: '마틴게일과 바스켓 익절', filename: 'secret-name.ex5' },
    { id: 'ut', type: 'indicator', title: 'UT Bot 시그널', description: 'ATR 기반 매수 신호' },
    { id: 'literal', type: 'indicator', title: '[.*] 가격 알림', description: '가격 도달 시 표시' },
    { id: 'helper', type: 'helper', title: 'UT Bot 도우미', description: 'ATR' },
  ]
  const ids = (kind, query) => libraryPage(items, kind, 1, query).items.map(item => item.id)
  assert.deepEqual(ids('ea', '마틴게일'), ['ea'])
  assert.deepEqual(ids('ea', '양방향돌파'), ['ea'])
  assert.deepEqual(ids('indicator', '  ut   BOT  atr '), ['ut'])
  assert.deepEqual(ids('indicator', 'ＵＴ'), ['ut'])
  assert.deepEqual(ids('ea', 'UT'), ['ut'])
  assert.deepEqual(ids('indicator', '마틴게일'), ['ea'])
  assert.deepEqual(ids('indicator', '[.*]'), ['literal'])
  assert.deepEqual(ids('ea', 'secret-name'), [])
  assert.deepEqual(ids('indicator', 'no-match'), [])
  assert.deepEqual(ids('indicator', '   '), ['ut', 'literal'])
})

test('English translations and original Korean are searchable before nine-item pagination', () => {
  const items = Array.from({ length: 20 }, (_, i) => ({
    id: `ea-${i}`, type: 'ea', title: `프로그램 ${i}`, description: i < 10 ? '예약주문 관리' : '청산 관리',
  }))
  const translate = text => text === '예약주문 관리' ? 'Pending order management' : text
  const first = libraryPage(items, 'ea', 1, 'PENDING', translate)
  const last = libraryPage(items, 'ea', 2, 'PENDING', translate)
  assert.equal(first.filteredItems.length, 10)
  assert.equal(first.pageCount, 2)
  assert.equal(first.items.length, 9)
  assert.deepEqual(last.items.map(item => item.id), ['ea-9'])
  assert.equal(libraryPage(items, 'ea', 1, '예약주문', translate).filteredItems.length, 10)
  assert.equal(libraryPage(items, 'ea', 3, 'no match', translate).page, 1)
})


test('combined search paginates both types, while clearing restores the original category', () => {
  const items = [
    ...Array.from({ length: 6 }, (_, i) => ({ id: `ea-${i}`, type: 'ea', title: `신호 EA ${i}`, description: '매매 신호' })),
    ...Array.from({ length: 6 }, (_, i) => ({ id: `indicator-${i}`, type: 'indicator', title: `신호 지표 ${i}`, description: '매매 신호' })),
    { id: 'helper', type: 'helper', title: '신호 인증 도우미' },
  ]
  for (const originalType of ['ea', 'indicator']) {
    const first = libraryPage(items, originalType, 1, '신호')
    const second = libraryPage(items, originalType, 2, '신호')
    assert.equal(first.filteredItems.length, 12)
    assert.equal(first.pageCount, 2)
    assert.equal(first.items.length, 9)
    assert.equal(second.items.length, 3)
    assert.deepEqual([...new Set(first.items.map(item => item.type))], ['ea', 'indicator'])
    const cleared = libraryPage(items, originalType, 1, '')
    assert.equal(cleared.items.length, 6)
    assert.ok(cleared.items.every(item => item.type === originalType))
    assert.deepEqual(libraryPage(items, originalType, 1, '   ').items, cleared.items)
  }
})

test('English content search reaches the other kind and still matches original Korean', () => {
  const items = [
    { id: 'ea', type: 'ea', title: '돌파 EA', description: '예약주문 관리' },
    { id: 'indicator', type: 'indicator', title: '매수매도 지표', description: '가격 신호' },
  ]
  const english = { '예약주문 관리': 'Pending order management', '매수매도 지표': 'Buy Sell Indicator', '가격 신호': 'Price signals' }
  const translate = text => english[text] || text
  assert.deepEqual(libraryPage(items, 'ea', 1, 'BUY SELL', translate).items.map(item => item.id), ['indicator'])
  assert.deepEqual(libraryPage(items, 'indicator', 1, 'pending', translate).items.map(item => item.id), ['ea'])
  assert.deepEqual(libraryPage(items, 'ea', 1, '가격', translate).items.map(item => item.id), ['indicator'])
})
