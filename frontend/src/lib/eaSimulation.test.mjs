import test from 'node:test'
import assert from 'node:assert/strict'
import { createSimulation, advanceSimulation, applyEa, floatingProfit, normalizeLot, MAX_HOLD_MS, MAX_HOLD_TICKS, TICK_INTERVAL_MS } from './eaSimulation.mjs'

function createActiveSimulation(random = Math.random) {
  const state = createSimulation(random)
  applyEa(state, random)
  return state
}
function withPosition(side, entry, price, lot = 0.1) {
  const state = createActiveSimulation(() => 0.5)
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
  assert.equal(reset.eaApplied, false)
  assert.equal(reset.tradeCount, 0)
  assert.equal(reset.entryCount, 0)
  assert.equal(reset.winCount, 0)
  assert.equal(reset.lossCount, 0)
})

test('long runs open and close trades, retain bounded data and valid OHLC', () => {
  let seed = 7
  const random = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646 }
  const state = createActiveSimulation(random)
  for (let i = 0; i < 10000; i++) advanceSimulation(state, 0.01, random)
  assert.ok(state.tradeCount > 20)
  assert.equal(state.entryCount, state.tradeCount + (state.position ? 1 : 0))
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
    const state = createActiveSimulation(() => 0.5)
    for (let i = 0; i < 4; i++) advanceSimulation(state, amount, () => 0.5)
    assert.equal(state.position.lot, amount)
  }
  assert.equal(normalizeLot('2.37'), 2.37)
  assert.equal(normalizeLot(0), 0.01)
  assert.equal(normalizeLot(-10), 0.01)
  assert.equal(normalizeLot(1000), 100)
  assert.equal(normalizeLot(1.234), 1.23)
  for (const value of ['', null, undefined, NaN, Infinity, 'invalid']) assert.equal(normalizeLot(value), 10)
})

test('default entries use ten lots and larger lots scale actual P/L', () => {
  const state = createActiveSimulation(() => 0.5)
  for (let i = 0; i < 4; i++) advanceSimulation(state, undefined, () => 0.5)
  assert.equal(state.position.lot, 10)
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4001, 1)), 80)
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4001, 100)), 8000)
})
test('timed exits count their realized outcome and entry levels match trade direction', () => {
  for (const side of ['BUY', 'SELL']) {
    const state = createActiveSimulation(() => 0.5)
    for (let i = 0; i < 4; i++) advanceSimulation(state, 1, () => 0.5)
    const p = state.position
    assert.ok(p.side === 'BUY' ? p.stop < p.entry && p.target > p.entry : p.stop > p.entry && p.target < p.entry)
    for (const gain of [true, false]) {
      const direction = side === 'BUY' ? 1 : -1
      const timed = withPosition(side, 4000, 4000 + direction * (gain ? 1 : -1))
      timed.position.openedAt = -MAX_HOLD_TICKS
      advanceSimulation(timed, 1, () => 0.5)
      assert.equal(timed.trades[0].reason, '시간 청산')
      assert.equal(timed.winCount, gain ? 1 : 0)
      assert.equal(timed.lossCount, gain ? 0 : 1)
    }
  }
})
test('cumulative trades count entries once and remain unchanged at exit', () => {
  const state = createActiveSimulation(() => 0.5)
  assert.equal(state.entryCount, 0)
  for (let i = 0; i < 4; i++) advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.entryCount, 1)
  assert.ok(state.position)
  const side = state.position.side === 'BUY' ? 1 : -1
  state.price = state.position.entry + side * 5
  advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.position, null)
  assert.equal(state.entryCount, 1)
  assert.equal(state.tradeCount, 1)
  for (let i = 0; i < 20 && state.entryCount < 2; i++) advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.entryCount, 2)
  assert.ok(state.position)
  advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.entryCount, 2)
})
test('an unchanged position remains open before four seconds and settles at four seconds', () => {
  assert.equal(MAX_HOLD_MS, 4000)
  assert.equal(MAX_HOLD_TICKS * TICK_INTERVAL_MS, 4000)
  const state = withPosition('BUY', 4000, 4000.2, 1)
  const expectedProfit = floatingProfit(state)
  for (let tick = 1; tick < MAX_HOLD_TICKS; tick++) {
    advanceSimulation(state, 1, () => 0.5)
    assert.ok(state.position)
    assert.equal(state.tradeCount, 0)
  }
  advanceSimulation(state, 1, () => 0.5)
  assert.equal(state.position, null)
  assert.equal(state.trades[0].reason, '시간 청산')
  assert.equal(state.trades[0].profit, expectedProfit)
  assert.equal(state.balance, 10000 + expectedProfit)
})

function seededRandom(seed) {
  let value = Math.imul(seed, 2654435761) >>> 0
  return () => {
    value = (Math.imul(value, 1664525) + 1013904223) >>> 0
    return value / 4294967296
  }
}

test('independent starts vary history, trends, first positions and realized win rates', () => {
  const paths = new Set(), firstSides = new Set(), rates = new Set(), volatility = new Set()
  let rising = 0, falling = 0, againstTrend = 0, profitableRuns = 0, losingRuns = 0
  for (let seed = 1; seed <= 80; seed++) {
    const random = seededRandom(seed)
    const state = createActiveSimulation(random)
    const historyMove = state.price - state.candles[0].open
    if (historyMove > 0) rising += 1
    if (historyMove < 0) falling += 1
    paths.add(state.candles.map(c => `${c.open}/${c.high}/${c.low}/${c.close}`).join(','))
    volatility.add(state.market.volatility)
    for (let tick = 0; tick < 6 && !state.position; tick++) advanceSimulation(state, 0.01, random)
    assert.ok(state.position)
    firstSides.add(state.position.side)
    if ((historyMove > 0 && state.position.side === 'SELL') || (historyMove < 0 && state.position.side === 'BUY')) againstTrend += 1
    for (let tick = 0; tick < 400; tick++) advanceSimulation(state, 0.01, random)
    assert.ok(state.tradeCount > 0)
    rates.add((state.winCount / state.tradeCount).toFixed(3))
    if (state.balance > 10000) profitableRuns += 1
    if (state.balance < 10000) losingRuns += 1
    assert.equal(state.entryCount, state.tradeCount + (state.position ? 1 : 0))
    assert.ok(state.winCount + state.lossCount <= state.tradeCount)
    assert.ok(Math.abs(state.equity - state.balance - floatingProfit(state)) < 0.011)
    for (let index = 1; index < state.candles.length; index++) {
      const current = state.candles[index], previous = state.candles[index - 1]
      assert.equal(current.open, previous.close)
      assert.ok(current.low <= current.open && current.low <= current.close)
      assert.ok(current.high >= current.open && current.high >= current.close)
    }
  }
  assert.equal(paths.size, 80)
  assert.equal(firstSides.size, 2)
  assert.ok(rising >= 20 && falling >= 20)
  assert.ok(againstTrend >= 20)
  assert.ok(volatility.size > 40)
  assert.ok(rates.size > 10)
  assert.ok(profitableRuns > 0 && losingRuns > 0)
})
test('unapplied EA lets the market run without orders, P/L or account changes', () => {
  const random = seededRandom(307)
  const state = createSimulation(random)
  const originalPrice = state.price
  const originalLastCandle = state.candles[state.candles.length - 1].id
  for (let tick = 0; tick < 240; tick++) advanceSimulation(state, 10, random)
  assert.equal(state.eaApplied, false)
  assert.equal(state.position, null)
  assert.equal(state.entryCount, 0)
  assert.equal(state.tradeCount, 0)
  assert.equal(state.winCount, 0)
  assert.equal(state.lossCount, 0)
  assert.equal(state.balance, 10000)
  assert.equal(state.equity, 10000)
  assert.equal(state.maxDrawdown, 0)
  assert.notEqual(state.price, originalPrice)
  assert.ok(state.candles[state.candles.length - 1].id > originalLastCandle)
  assert.ok(state.candles.length <= 64)
})

test('EA applies once to the current market and only resets with a new session', () => {
  const state = createSimulation(() => 0.5)
  for (let tick = 0; tick < 100; tick++) advanceSimulation(state, 10, () => 0.5)
  const currentPrice = state.price, history = state.candles
  applyEa(state, () => 0.5)
  assert.equal(state.eaApplied, true)
  assert.equal(state.price, currentPrice)
  assert.equal(state.candles, history)
  assert.equal(state.tick, 100)
  assert.equal(state.position, null)
  const firstEntryTick = state.firstEntryTick
  applyEa(state, () => { throw new Error('Applying twice must not reschedule the EA') })
  assert.equal(state.firstEntryTick, firstEntryTick)
  for (let tick = 0; tick < 3; tick++) advanceSimulation(state, 10, () => 0.5)
  assert.equal(state.position, null)
  advanceSimulation(state, 10, () => 0.5)
  assert.equal(state.entryCount, 1)
  assert.ok(state.position)
  const side = state.position.side === 'BUY' ? 1 : -1
  state.price = state.position.entry + side * 5
  advanceSimulation(state, 10, () => 0.5)
  assert.equal(state.position, null)
  assert.equal(state.eaApplied, true)
  const reset = createSimulation(() => 0.5)
  assert.equal(reset.eaApplied, false)
  assert.equal(reset.position, null)
  assert.equal(reset.entryCount, 0)
  assert.equal(reset.tradeCount, 0)
  assert.equal(reset.balance, 10000)
})