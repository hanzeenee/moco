// Entirely synthetic prices and orders. No broker, account or network connection.
const SPREAD = 0.2
const CONTRACT_SIZE = 100
const INITIAL_BALANCE = 10000
export const DEFAULT_LOT = 10
export const CANDLE_MINUTES = 5
export const TICK_INTERVAL_MS = 250
export const MAX_HOLD_MS = 4000
export const MAX_HOLD_TICKS = MAX_HOLD_MS / TICK_INTERVAL_MS
export const STOP_DISTANCE = 2.4
export const TARGET_DISTANCE = 3.6

const round = value => Math.round(value * 100) / 100
const sideSign = side => side === 'BUY' ? 1 : -1
const precisePrice = value => Math.round(value * 1e8) / 1e8
const exitPrice = (price, side) => precisePrice(price - sideSign(side) * SPREAD / 2)
const entryDelay = random => 2 + Math.floor(random() * 5)

// Direction, strength, duration and volatility have no fixed phase or cycle.
function newRegime(random) {
  const direction = Math.floor(random() * 3) - 1
  return {
    drift: direction * (0.06 + random() * 0.42),
    volatility: 0.25 + random() * 1.05,
    remainingTicks: 8 + Math.floor(random() * 65)
  }
}

// History and live candles use the same stochastic process and continuous price.
function nextPrice(market, price, random) {
  if (market.remainingTicks <= 0) Object.assign(market, newRegime(random))
  market.remainingTicks -= 1
  const scale = market.volatility * (0.5 + random())
  const noise = (random() + random() - 1) * scale * 1.8
  const jump = random() < 0.025 ? (random() - 0.5) * market.volatility * 6 : 0
  return round(Math.max(100, price + market.drift + noise + jump))
}

// A synthetic trade scene: random bends/noise, with the chosen TP/SL reached at 4s.
function tradeScenePrice(position, tick, previousPrice, marketPrice) {
  const elapsed = tick - position.openedAt
  const level = position.exitTarget === 'TP' ? position.target : position.stop
  const quoteShift = sideSign(position.side) * SPREAD / 2
  const destination = round(level + quoteShift)
  if (elapsed >= MAX_HOLD_TICKS) return destination
  const progress = elapsed / MAX_HOLD_TICKS
  const curvedProgress = progress + position.pathBend * progress * (1 - progress)
  position.pathOffset = Math.max(-0.7, Math.min(0.7, position.pathOffset * 0.65 + (marketPrice - previousPrice) * position.pathNoise * 0.35))
  const price = position.pathStart + (destination - position.pathStart) * curvedProgress + position.pathOffset * 4 * progress * (1 - progress)
  // Stay inside both visible levels and executable quote levels until the final tick.
  const lower = Math.min(position.stop, position.target) + Math.max(0, quoteShift) + 0.02
  const upper = Math.max(position.stop, position.target) + Math.min(0, quoteShift) - 0.02
  return round(Math.max(lower, Math.min(upper, price)))
}
export function normalizeLot(value) {
  const amount = Number(value)
  if (value === '' || value === null || !Number.isFinite(amount)) return DEFAULT_LOT
  return round(Math.min(100, Math.max(0.01, amount)))
}

export function floatingProfit(state) {
  const p = state.position
  return p ? round((exitPrice(state.price, p.side) - p.entry) * sideSign(p.side) * p.lot * CONTRACT_SIZE) : 0
}

export function createSimulation(random = Math.random) {
  const market = newRegime(random)
  const candles = []
  let price = round(4000 + (random() - 0.5) * 80)
  for (let i = 0; i < 48; i++) {
    const open = price
    let high = open, low = open
    for (let tick = 0; tick < 4; tick++) {
      price = nextPrice(market, price, random)
      high = Math.max(high, price)
      low = Math.min(low, price)
    }
    candles.push({ id: i, open, close: price, high, low })
  }
  return {
    price, candles, market, tick: 0, nextCandle: 48, firstEntryTick: null, eaApplied: false,
    balance: INITIAL_BALANCE, equity: INITIAL_BALANCE, peakEquity: INITIAL_BALANCE, maxDrawdown: 0,
    position: null, trades: [], tradeCount: 0, entryCount: 0, winCount: 0, lossCount: 0, cooldown: 0,
    status: 'EA 미적용 · 차트만 실행 중', bankrupt: false
  }
}

// Activation is one-way for this session; only a fresh simulation removes the EA.
export function applyEa(state, random = Math.random) {
  if (state.eaApplied || state.bankrupt) return state
  state.eaApplied = true
  state.firstEntryTick = state.tick + entryDelay(random)
  state.status = 'EA 적용 완료 · 진입 대기'
  return state
}
function updateAccount(state) {
  state.equity = Math.max(0, round(state.balance + floatingProfit(state)))
  state.peakEquity = Math.max(state.peakEquity, state.equity)
  state.maxDrawdown = Math.max(state.maxDrawdown, (state.peakEquity - state.equity) / state.peakEquity * 100)
}

// Stop at the zero-equity boundary instead of showing a negative account.
function capAtZeroEquity(state) {
  const position = state.position
  if (!position || state.balance + floatingProfit(state) > 0) return false
  const direction = sideSign(position.side)
  const level = position.entry - direction * state.balance / (position.lot * CONTRACT_SIZE)
  state.price = precisePrice(level + direction * SPREAD / 2)
  return true
}

function updateCurrentCandle(state) {
  const candle = state.candles[state.candles.length - 1]
  candle.close = state.price
  candle.high = Math.max(candle.high, state.price)
  candle.low = Math.min(candle.low, state.price)
}

function closePosition(state, exitTarget, random) {
  const position = state.position
  const exhausted = exitTarget === 'OUT'
  const pnl = exhausted ? -state.balance : floatingProfit(state)
  const reason = exhausted ? '평가금 소진' : exitTarget === 'TP' ? '익절' : '손절'
  state.balance = Math.max(0, round(state.balance + pnl))
  state.tradeCount += 1
  if (pnl > 0) state.winCount += 1
  if (pnl < 0) state.lossCount += 1
  state.trades.unshift({ ...position, exitTarget, id: state.tradeCount, exit: exitPrice(state.price, position.side), exitMid: state.price, closedAt: state.tick, exitCandleId: state.candles[state.candles.length - 1].id, profit: pnl, reason })
  state.trades = state.trades.slice(0, 20)
  state.position = null
  state.bankrupt = exhausted || state.balance <= 0
  state.cooldown = state.bankrupt ? 0 : entryDelay(random)
  state.status = state.bankrupt ? '평가금 0 · 체험 종료' : `${reason} 완료 · 다음 진입 대기`
}

// Four active ticks form one virtual M5 candle. Hidden tabs do not advance.
export function advanceSimulation(state, lot = DEFAULT_LOT, random = Math.random) {
  if (state.bankrupt) return state
  state.tick += 1
  const previousPrice = state.price
  const marketPrice = nextPrice(state.market, previousPrice, random)
  state.price = state.position ? tradeScenePrice(state.position, state.tick, previousPrice, marketPrice) : marketPrice
  const exhausted = capAtZeroEquity(state)
  if ((state.tick - 1) % 4 === 0) {
    state.candles.push({ id: state.nextCandle++, open: previousPrice, high: Math.max(previousPrice, state.price), low: Math.min(previousPrice, state.price), close: state.price })
    if (state.candles.length > 64) state.candles.shift()
  } else {
    updateCurrentCandle(state)
  }
  if (!state.eaApplied) return state

  updateAccount(state)
  if (state.position) {
    const position = state.position
    if (exhausted) {
      closePosition(state, 'OUT', random)
    } else if (state.tick - position.openedAt >= MAX_HOLD_TICKS) {
      closePosition(state, position.exitTarget, random)
    } else {
      state.status = `${position.side === 'BUY' ? '매수' : '매도'} 보유 중 · 익절/손절 감시`
    }
  } else if (state.cooldown > 0) {
    state.cooldown -= 1
  } else if (state.tick >= state.firstEntryTick) {
    const side = random() < 0.5 ? 'BUY' : 'SELL'
    const entry = round(state.price + sideSign(side) * SPREAD / 2)
    state.entryCount += 1
    state.position = {
      side, entry, lot: normalizeLot(lot), openedAt: state.tick,
      candleId: state.candles[state.candles.length - 1].id,
      exitTarget: random() < 0.5 ? 'TP' : 'SL',
      pathStart: state.price, pathBend: (random() - 0.5) * 1.2, pathNoise: 0.2 + random() * 0.65, pathOffset: 0,
      stop: round(entry - sideSign(side) * STOP_DISTANCE),
      target: round(entry + sideSign(side) * TARGET_DISTANCE)
    }
    state.status = `${side === 'BUY' ? '매수' : '매도'} 진입 · 가상 EA 실행`
    // A large lot can exhaust the account immediately through the spread.
    if (capAtZeroEquity(state)) {
      updateCurrentCandle(state)
      closePosition(state, 'OUT', random)
    }
  }
  updateAccount(state)
  return state
}
