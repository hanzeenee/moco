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
const exitPrice = (price, side) => round(price - sideSign(side) * SPREAD / 2)
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
    price, candles, market, tick: 0, nextCandle: 48, firstEntryTick: entryDelay(random),
    balance: INITIAL_BALANCE, equity: INITIAL_BALANCE, peakEquity: INITIAL_BALANCE, maxDrawdown: 0,
    position: null, trades: [], tradeCount: 0, entryCount: 0, winCount: 0, lossCount: 0, cooldown: 0,
    status: 'EA 준비 중 · 진입 대기', bankrupt: false
  }
}

// Four active ticks form one virtual M5 candle. Paused/hidden tabs do not advance.
export function advanceSimulation(state, lot = DEFAULT_LOT, random = Math.random) {
  if (state.bankrupt) return state
  state.tick += 1
  const previousPrice = state.price
  state.price = nextPrice(state.market, previousPrice, random)
  if ((state.tick - 1) % 4 === 0) {
    state.candles.push({ id: state.nextCandle++, open: previousPrice, high: Math.max(previousPrice, state.price), low: Math.min(previousPrice, state.price), close: state.price })
    if (state.candles.length > 64) state.candles.shift()
  } else {
    const candle = state.candles[state.candles.length - 1]
    candle.close = state.price
    candle.high = Math.max(candle.high, state.price)
    candle.low = Math.min(candle.low, state.price)
  }

  let pnl = floatingProfit(state)
  state.equity = round(state.balance + pnl)
  state.peakEquity = Math.max(state.peakEquity, state.equity)
  state.maxDrawdown = Math.max(state.maxDrawdown, (state.peakEquity - state.equity) / state.peakEquity * 100)

  if (state.position) {
    const position = state.position
    const movement = (exitPrice(state.price, position.side) - position.entry) * sideSign(position.side)
    const reason = movement <= -STOP_DISTANCE ? '손절' : movement >= TARGET_DISTANCE ? '익절' : state.tick - position.openedAt >= MAX_HOLD_TICKS ? '시간 청산' : state.equity <= 0 ? '잔고 소진' : null
    if (reason) {
      state.balance = round(state.balance + pnl)
      state.tradeCount += 1
      if (pnl > 0) state.winCount += 1
      if (pnl < 0) state.lossCount += 1
      state.trades.unshift({ ...position, id: state.tradeCount, exit: exitPrice(state.price, position.side), profit: pnl, reason })
      state.trades = state.trades.slice(0, 20)
      state.position = null
      state.cooldown = entryDelay(random)
      state.status = `${reason} 완료 · 다음 진입 대기`
      state.bankrupt = state.balance <= 0
    } else {
      state.status = `${position.side === 'BUY' ? '매수' : '매도'} 보유 중 · 익절/손절 감시`
    }
  } else if (state.cooldown > 0) {
    state.cooldown -= 1
  } else if (state.tick >= state.firstEntryTick) {
    // Sample every entry independently of history, trend, prior side or outcome.
    const side = random() < 0.5 ? 'BUY' : 'SELL'
    const entry = round(state.price + sideSign(side) * SPREAD / 2)
    state.entryCount += 1
    state.position = {
      side, entry, lot: normalizeLot(lot), openedAt: state.tick,
      candleId: state.candles[state.candles.length - 1].id,
      stop: round(entry - sideSign(side) * STOP_DISTANCE),
      target: round(entry + sideSign(side) * TARGET_DISTANCE)
    }
    state.status = `${side === 'BUY' ? '매수' : '매도'} 진입 · 가상 EA 실행`
  }
  pnl = floatingProfit(state)
  state.equity = round(state.balance + pnl)
  state.peakEquity = Math.max(state.peakEquity, state.equity)
  state.maxDrawdown = Math.max(state.maxDrawdown, (state.peakEquity - state.equity) / state.peakEquity * 100)
  if (state.bankrupt) state.status = '가상 잔고 소진 · 다시 시작해 주세요'
  return state
}
