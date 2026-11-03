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
