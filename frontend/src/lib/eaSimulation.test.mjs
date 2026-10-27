import test from 'node:test'
import assert from 'node:assert/strict'
import { createSimulation, advanceSimulation, applyEa, floatingProfit, normalizeLot, MAX_HOLD_MS, MAX_HOLD_TICKS, TICK_INTERVAL_MS, STOP_DISTANCE, TARGET_DISTANCE } from './eaSimulation.mjs'

function activeSimulation(random = Math.random) {
  const state = createSimulation(random)
  applyEa(state, random)
  return state
}

function withPosition(side, entry, price, lot = 0.1, exitTarget = 'TP') {
  const state = activeSimulation(() => 0.5)
  const direction = side === 'BUY' ? 1 : -1
  Object.assign(state, { price, entryCount: 1, position: {
    side, entry, lot, openedAt: 0, candleId: 47, exitTarget,
    stop: Math.round((entry - direction * STOP_DISTANCE) * 100) / 100,
    target: Math.round((entry + direction * TARGET_DISTANCE) * 100) / 100,
    pathStart: price, pathBend: 0, pathNoise: 0.5, pathOffset: 0
  } })
  return state
}

function seededRandom(seed) {
  let value = Math.imul(seed, 2654435761) >>> 0
  return () => { value = (Math.imul(value, 1664525) + 1013904223) >>> 0; return value / 4294967296 }
}

test('spread and contract size determine floating P/L', () => {
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4001)), 8)
  assert.equal(floatingProfit(withPosition('SELL', 3999.9, 3999)), 8)
  assert.equal(floatingProfit(withPosition('BUY', 4000.1, 4000)), -2)
})

for (const side of ['BUY', 'SELL']) {
  for (const exitTarget of ['TP', 'SL']) {
    test(`${side} reaches ${exitTarget} at four seconds and settles once at the exact level`, () => {
      const state = withPosition(side, 4000, 4000, 0.05, exitTarget)
      const position = { ...state.position }
      for (let tick = 1; tick < MAX_HOLD_TICKS; tick++) {
        advanceSimulation(state, 100, () => 0.5)
        assert.ok(state.position)
        assert.equal(state.tradeCount, 0)
        assert.ok(state.price > Math.min(position.stop, position.target))
        assert.ok(state.price < Math.max(position.stop, position.target))
      }
      const previousPrice = state.price
      advanceSimulation(state, 100, () => 0.5)
      const closed = state.trades[0]
      assert.equal(closed.closedAt - closed.openedAt, MAX_HOLD_TICKS)
      assert.equal(closed.exit, exitTarget === 'TP' ? position.target : position.stop)
      assert.equal(closed.profit, exitTarget === 'TP' ? 18 : -12)
      assert.equal(closed.reason, exitTarget === 'TP' ? '익절' : '손절')
      assert.equal(closed.lot, 0.05)
      assert.equal(closed.exitMid, state.price)
      assert.equal(closed.exitCandleId, state.candles[state.candles.length - 1].id)
      assert.ok(Math.abs(state.price - previousPrice) < 1)
      assert.equal(state.balance, 10000 + closed.profit)
      assert.equal(state.equity, state.balance)
      assert.equal(state.winCount, exitTarget === 'TP' ? 1 : 0)
      assert.equal(state.lossCount, exitTarget === 'SL' ? 1 : 0)
      assert.equal(state.position, null)
      advanceSimulation(state, 100, () => 0.5)
      assert.equal(state.tradeCount, 1)
    })
  }
}

test('extreme market noise cannot trigger an early exit or push the scene past SL/TP', () => {
  assert.equal(MAX_HOLD_MS, 4000)
  assert.equal(MAX_HOLD_TICKS * TICK_INTERVAL_MS, 4000)
  for (const side of ['BUY', 'SELL']) {
    for (const exitTarget of ['TP', 'SL']) {
      const state = withPosition(side, 4000, 4000, 1, exitTarget)
      state.position.pathBend = -0.6
      state.position.pathNoise = 0.85
      for (let tick = 1; tick < MAX_HOLD_TICKS; tick++) {
        advanceSimulation(state, 1, () => tick % 2 ? 0 : 0.999)
        assert.ok(state.position)
        const { stop, target } = state.position
        assert.ok(state.price > Math.min(stop, target) && state.price < Math.max(stop, target))
      }
      advanceSimulation(state, 1, () => 0.999)
      assert.equal(state.position, null)
      assert.equal(state.trades[0].reason, exitTarget === 'TP' ? '익절' : '손절')
    }
  }
})

test('drawdown includes open losses and a fresh session resets the account and EA', () => {
  const state = withPosition('BUY', 4000, 3999)
  advanceSimulation(state, 1, () => 0.5)
  assert.ok(state.equity < state.balance)
  assert.ok(state.maxDrawdown > 0)
  const reset = createSimulation(() => 0.5)
  assert.equal(reset.balance, 10000)
  assert.equal(reset.maxDrawdown, 0)
  assert.equal(reset.position, null)
  assert.equal(reset.eaApplied, false)
  assert.equal(reset.entryCount + reset.tradeCount + reset.winCount + reset.lossCount, 0)
})

test('zero equity closes immediately before the four-second SL scene completes', () => {
  for (const side of ['BUY', 'SELL']) {
    const state = withPosition(side, 4000, 4000, 100, 'SL')
    let closedAfter = 0
    for (let tick = 1; tick <= MAX_HOLD_TICKS; tick++) {
      advanceSimulation(state, 100, () => 0.5)
      assert.ok(state.equity >= 0)
      if (state.bankrupt) { closedAfter = tick; break }
      assert.ok(state.equity > 0)
    }
    assert.ok(closedAfter > 0 && closedAfter < MAX_HOLD_TICKS)
    assert.equal(state.position, null)
    assert.equal(state.equity, 0)
    assert.equal(state.balance, 0)
    assert.equal(state.maxDrawdown, 100)
    assert.equal(state.trades[0].reason, '평가금 소진')
    assert.equal(state.trades[0].exitTarget, 'OUT')
    assert.equal(state.trades[0].profit, -10000)
    assert.equal(state.trades[0].exit, side === 'BUY' ? 3999 : 4001)
    const tick = state.tick, price = state.price, trades = state.entryCount
    for (let i = 0; i < 20; i++) advanceSimulation(state, 100, () => 0.5)
    assert.equal(state.tick, tick)
    assert.equal(state.price, price)
    assert.equal(state.entryCount, trades)
  }
})

test('manual lot range, default ten lots and input normalization stay intact', () => {
  for (const amount of [0.01, 0.25, 1, 12.34, 100, undefined]) {
    const state = activeSimulation(() => 0.5)
    for (let tick = 0; tick < 4; tick++) advanceSimulation(state, amount, () => 0.5)
    assert.equal(state.position.lot, amount ?? 10)
  }
  assert.equal(normalizeLot('2.37'), 2.37)
  assert.equal(normalizeLot(0), 0.01)
  assert.equal(normalizeLot(-10), 0.01)
  assert.equal(normalizeLot(1000), 100)
  assert.equal(normalizeLot(1.234), 1.23)
  for (const value of ['', null, undefined, NaN, Infinity, 'invalid']) assert.equal(normalizeLot(value), 10)
})

test('cumulative entries increase on entry and persist through completed scenes', () => {
  const state = activeSimulation(() => 0.5)
  for (let tick = 0; tick < 4; tick++) advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.entryCount, 1)
  for (let tick = 0; tick < MAX_HOLD_TICKS; tick++) advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.position, null)
  assert.equal(state.entryCount, 1)
  assert.equal(state.tradeCount, 1)
  for (let tick = 0; tick < 10 && !state.position; tick++) advanceSimulation(state, 0.01, () => 0.5)
  assert.equal(state.entryCount, 2)
  assert.ok(state.position)
})

test('long runs preserve OHLC, accounting, bounded history and exact TP/SL prices', () => {
  const random = seededRandom(103)
  const state = activeSimulation(random)
  for (let tick = 0; tick < 10000; tick++) advanceSimulation(state, 0.01, random)
  assert.ok(state.tradeCount > 20)
  assert.equal(state.entryCount, state.tradeCount + (state.position ? 1 : 0))
  assert.equal(state.winCount + state.lossCount, state.tradeCount)
  assert.equal(state.trades.length, 20)
  assert.ok(state.candles.length <= 64)
  assert.ok(Math.abs(state.equity - state.balance - floatingProfit(state)) < 0.011)
  for (const trade of state.trades) {
    assert.equal(trade.closedAt - trade.openedAt, MAX_HOLD_TICKS)
    assert.equal(trade.exit, trade.exitTarget === 'TP' ? trade.target : trade.stop)
    assert.ok(['익절', '손절'].includes(trade.reason))
  }
  for (let i = 0; i < state.candles.length; i++) {
    const c = state.candles[i]
    assert.ok(c.low <= c.open && c.low <= c.close && c.high >= c.open && c.high >= c.close)
    if (i > 0) assert.equal(c.open, state.candles[i - 1].close)
  }
})

test('independent starts vary history, directions, scene paths and win rates', () => {
  const paths = new Set(), sides = new Set(), rates = new Set(), bends = new Set(), outcomes = new Set()
  let rising = 0, falling = 0
  for (let seed = 1; seed <= 80; seed++) {
    const random = seededRandom(seed)
    const state = activeSimulation(random)
    const historyMove = state.price - state.candles[0].open
    if (historyMove > 0) rising++
    if (historyMove < 0) falling++
    paths.add(state.candles.map(c => `${c.open}/${c.high}/${c.low}/${c.close}`).join(','))
    for (let tick = 0; tick < 6 && !state.position; tick++) advanceSimulation(state, 0.01, random)
    sides.add(state.position.side)
    bends.add(state.position.pathBend)
    outcomes.add(state.position.exitTarget)
    for (let tick = 0; tick < 400; tick++) advanceSimulation(state, 0.01, random)
    rates.add((state.winCount / state.tradeCount).toFixed(3))
  }
  assert.equal(paths.size, 80)
  assert.equal(sides.size, 2)
  assert.equal(outcomes.size, 2)
  assert.ok(rising >= 20 && falling >= 20)
  assert.ok(bends.size > 40)
  assert.ok(rates.size > 10)
})

test('unapplied EA moves the market without starting trades or changing the account', () => {
  const random = seededRandom(307)
  const state = createSimulation(random)
  const originalPrice = state.price
  for (let tick = 0; tick < 240; tick++) advanceSimulation(state, 10, random)
  assert.equal(state.eaApplied, false)
  assert.equal(state.position, null)
  assert.equal(state.entryCount + state.tradeCount + state.winCount + state.lossCount, 0)
  assert.equal(state.balance, 10000)
  assert.equal(state.equity, 10000)
  assert.equal(state.maxDrawdown, 0)
  assert.notEqual(state.price, originalPrice)
})

test('EA applies once to the current market and remains applied after TP/SL', () => {
  const state = createSimulation(() => 0.5)
  for (let tick = 0; tick < 100; tick++) advanceSimulation(state, 10, () => 0.5)
  const price = state.price, candles = state.candles
  applyEa(state, () => 0.5)
  assert.equal(state.price, price)
  assert.equal(state.candles, candles)
  const firstTick = state.firstEntryTick
  applyEa(state, () => { throw new Error('Applying twice must not change the scene') })
  assert.equal(state.firstEntryTick, firstTick)
  for (let tick = 0; tick < 4; tick++) advanceSimulation(state, 10, () => 0.5)
  assert.equal(state.entryCount, 1)
  for (let tick = 0; tick < MAX_HOLD_TICKS; tick++) advanceSimulation(state, 10, () => 0.5)
  assert.equal(state.position, null)
  assert.equal(state.eaApplied, true)
  assert.equal(createSimulation(() => 0.5).eaApplied, false)
})

test('a fractional-lot stop-out reaches exactly zero without a negative cash balance', () => {
  const state = withPosition('BUY', 4000, 4000, 0.37, 'SL')
  state.balance = 37.43
  for (let tick = 0; tick < MAX_HOLD_TICKS && !state.bankrupt; tick++) advanceSimulation(state, 0.37, () => 0.5)
  assert.equal(state.bankrupt, true)
  assert.equal(state.equity, 0)
  assert.equal(state.balance, 0)
  const trade = state.trades[0]
  assert.equal(trade.profit, -37.43)
  assert.ok(Math.abs(Math.round((trade.exit - trade.entry) * trade.lot * 100 * 100) / 100 - trade.profit) < 0.011)
})

test('entry spread can end an exhausted account on the entry tick', () => {
  const state = activeSimulation(() => 0.5)
  state.balance = 50
  for (let tick = 0; tick < 4; tick++) advanceSimulation(state, 100, () => 0.5)
  assert.equal(state.bankrupt, true)
  assert.equal(state.position, null)
  assert.equal(state.equity, 0)
  assert.equal(state.balance, 0)
  assert.equal(state.entryCount, 1)
  assert.equal(state.tradeCount, 1)
  assert.equal(state.trades[0].closedAt, state.trades[0].openedAt)
  assert.equal(state.trades[0].exitTarget, 'OUT')
  assert.equal(state.trades[0].profit, -50)
})