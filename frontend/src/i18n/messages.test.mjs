import test from 'node:test'
import assert from 'node:assert/strict'
import { english, normalizeLocale, translate } from './messages.mjs'
import { createSimulation, applyEa, advanceSimulation } from '../lib/eaSimulation.mjs'

test('unsupported saved preferences use Korean; identifiers and unknown content are preserved', () => {
  for (const value of [undefined, null, '', 'fr', '<script>']) assert.equal(normalizeLocale(value), 'ko')
  assert.equal(normalizeLocale('en'), 'en')
  assert.equal(translate('XAUUSD', 'en'), 'XAUUSD')
  assert.equal(translate('MOCONIX', 'ko'), 'MOCONIX')
})

test('all translated copy is nonempty English and preserves interpolation fields', () => {
  const fields = value => [...value.matchAll(/\{(\w+)\}/g)].map(match => match[1]).sort()
  for (const [korean, translated] of Object.entries(english)) {
    assert.ok(translated.trim(), korean)
    assert.doesNotMatch(translated, /[가-힣]/u, korean)
    assert.deepEqual(fields(translated), fields(korean), korean)
  }
  assert.equal(translate('익절 {count}회', 'ko', { count: 0 }), '익절 0회')
  assert.equal(translate('익절 {count}회', 'en', { count: 12 }), 'TP 12')
})

test('live simulation statuses remain translated through entry, TP, SL and exhaustion', () => {
  const seen = new Set()
  for (let seed = 1; seed <= 8; seed += 1) {
    let randomState = seed
    const random = () => { randomState = randomState * 16807 % 2147483647; return (randomState - 1) / 2147483646 }
    const state = createSimulation(random)
    seen.add(state.status)
    applyEa(state, random)
    seen.add(state.status)
    for (let tick = 0; tick < 2000 && !state.bankrupt; tick += 1) {
      advanceSimulation(state, seed === 8 ? 100 : 1, random)
      seen.add(state.status)
    }
  }
  const exhausted = createSimulation(() => 0.5)
  exhausted.balance = 1
  exhausted.equity = 1
  applyEa(exhausted, () => 0.5)
  for (let tick = 0; tick < 100 && !exhausted.bankrupt; tick += 1) advanceSimulation(exhausted, 100, () => 0.5)
  seen.add(exhausted.status)
  for (const status of seen) assert.doesNotMatch(translate(status, 'en'), /[가-힣]/u, status)
  assert.ok([...seen].some(status => status.startsWith('익절 완료')))
  assert.ok([...seen].some(status => status.startsWith('손절 완료')))
  assert.ok(seen.has('평가금 0 · 체험 종료'))
})
