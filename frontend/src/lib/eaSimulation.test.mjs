import test from 'node:test'
import assert from 'node:assert/strict'
import { createSimulation, advanceSimulation, floatingProfit, normalizeLot } from './eaSimulation.mjs'

function withPosition(side, entry, price, lot = 0.1) {
  const state = createSimulation(() => 0.5)
  Object.assign(state, { price, position: { side, entry, lot, openedAt: 0, candleId: 47 } })
  return state
}

test('spread and contract size produce executable floating P/L for both sides', () => {
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4001)), 8)
  assert.equal(floatingProfit(withPosition('SELL', 3999.9, 3999)), 8)
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4000)), -2)
})

for (const side of ['BUY', 'SELL']) {
  for (const outcome of ['익절', '손절']) {
    test(`${side} ${outcome} settles once and uses the position's original lot`, () => {
      const direction = side === 'BUY' ? 1 : -1
      const state = withPosition(side, 4000, 4000 + direction * (outcome === '익절' ? 5 : -4), 0.05)
      advanceSimulation(state, 0.1, () => 0.5)
      const closed = state.trades[0]
      assert.equal(closed.reason, outcome)
      assert.equal(state.winCount, outcome === '익절' ? 1 : 0)
      assert.equal(state.lossCount, outcome === '손절' ? 1 : 0)
      assert.equal(closed.lot, 0.05)
      assert.equal(state.balance, 10000 + closed.profit)
      assert.equal(state.equity, state.balance)
      assert.equal(state.position, null)
      assert.equal(state.tradeCount, 1)
      advanceSimulation(state, 0.1, () => 0.5)
      assert.equal(state.tradeCount, 1)
      assert.equal(state.balance, 10000 + closed.profit)
    })
  }
}

test('drawdown includes open losses and reset returns a fresh independent account', () => {
  const state = withPosition('BUY', 4000, 3999)
  advanceSimulation(state, 0.1, () => 0.5)
  assert.ok(state.equity < state.balance)
  assert.ok(state.maxDrawdown > 0)
  const reset = createSimulation(() => 0.5)
  assert.equal(reset.balance, 10000)
  assert.equal(reset.maxDrawdown, 0)
  assert.equal(reset.position, null)
  assert.equal(reset.tradeCount, 0)
  assert.equal(reset.winCount, 0)
  assert.equal(reset.lossCount, 0)
})

test('long runs open and close trades, retain bounded data and valid OHLC', () => {
  let seed = 7
  const random = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646 }
  const state = createSimulation(random)
  for (let i = 0; i < 10000; i++) advanceSimulation(state, 0.01, random)
  assert.ok(state.tradeCount > 20)
  assert.ok(state.winCount + state.lossCount > 20)
  assert.ok(state.winCount + state.lossCount <= state.tradeCount)
  assert.ok(state.trades.length <= 20)
  assert.ok(state.candles.length <= 64)
  assert.ok(Number.isFinite(state.equity))
  assert.ok(Math.abs(state.equity - state.balance - floatingProfit(state)) < 0.011)
  for (const c of state.candles) {
    assert.ok(c.low <= c.open && c.low <= c.close)
    assert.ok(c.high >= c.open && c.high >= c.close)
  }
})

test('exhausted account stops ticking until a new simulation is created', () => {
  const state = withPosition('BUY', 4000, 3996)
  state.balance = 1
  advanceSimulation(state, 0.1, () => 0.5)
  assert.equal(state.bankrupt, true)
  const tick = state.tick
  advanceSimulation(state, 0.1, () => 0.5)
  assert.equal(state.tick, tick)
})

test('manual lot input supports the full range and normalizes invalid entries', () => {
  for (const amount of [0.01, 0.25, 1, 12.34, 100]) {
    const state = createSimulation(() => 0.5)
    for (let i = 0; i < 4; i++) advanceSimulation(state, amount, () => 0.5)
    assert.equal(state.position.lot, amount)
  }
  assert.equal(normalizeLot('2.37'), 2.37)
  assert.equal(normalizeLot(0), 0.01)
  assert.equal(normalizeLot(-10), 0.01)
  assert.equal(normalizeLot(1000), 100)
  assert.equal(normalizeLot(1.234), 1.23)
  for (const value of ['', null, undefined, NaN, Infinity, 'invalid']) assert.equal(normalizeLot(value), 1)
})

test('default entries use one lot and larger lots scale actual P/L', () => {
  const state = createSimulation(() => 0.5)
  for (let i = 0; i < 4; i++) advanceSimulation(state, undefined, () => 0.5)
  assert.equal(state.position.lot, 1)
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4001, 1)), 80)
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4001, 100)), 8000)
})
test('timed exits count their realized outcome and entry levels match trade direction', () => {
  for (const side of ['BUY', 'SELL']) {
    const state = createSimulation(() => 0.5)
    for (let i = 0; i < 4; i++) advanceSimulation(state, 1, () => 0.5)
    const p = state.position
    assert.ok(p.side === 'BUY' ? p.stop < p.entry && p.target > p.entry : p.stop > p.entry && p.target < p.entry)
    for (const gain of [true, false]) {
      const direction = side === 'BUY' ? 1 : -1
      const timed = withPosition(side, 4000, 4000 + direction * (gain ? 1 : -1))
      timed.position.openedAt = -32
      advanceSimulation(timed, 1, () => 0.5)
      assert.equal(timed.trades[0].reason, '시간 청산')
      assert.equal(timed.winCount, gain ? 1 : 0)
      assert.equal(timed.lossCount, gain ? 0 : 1)
    }
  }
})