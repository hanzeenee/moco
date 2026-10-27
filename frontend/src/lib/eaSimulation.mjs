// Entirely synthetic prices and orders. No broker, account or network connection.
const SPREAD = 0.2
const CONTRACT_SIZE = 100
const INITIAL_BALANCE = 10000
export const DEFAULT_LOT = 1
export const CANDLE_MINUTES = 5
export const TICK_INTERVAL_MS = 250
export const STOP_DISTANCE = 2.4
export const TARGET_DISTANCE = 3.6

const round = value => Math.round(value * 100) / 100
const average = values => values.reduce((sum, value) => sum + value, 0) / values.length
const sideSign = side => side === 'BUY' ? 1 : -1
const exitPrice = (price, side) => round(price - sideSign(side) * SPREAD / 2)

// Clamp committed input to 0.01–100 lots with two decimal places.
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
  const candles = []
  let price = 4000
  for (let i = 0; i < 48; i++) {
    const open = price
    price = round(open + Math.sin(i / 5) * 0.38 + (random() - 0.5) * 1.2)
    candles.push({ id: i, open, close: price, high: round(Math.max(open, price) + random() * 0.7), low: round(Math.min(open, price) - random() * 0.7) })
  }
  return {
    price, candles, tick: 0, nextCandle: 48, balance: INITIAL_BALANCE,
    equity: INITIAL_BALANCE, peakEquity: INITIAL_BALANCE, maxDrawdown: 0,
    position: null, trades: [], tradeCount: 0, cooldown: 0,
    status: '시세 분석 중 · 진입 조건 확인', bankrupt: false
  }
}

// One call advances one simulated tick; four ticks form one virtual five-minute candle.
export function advanceSimulation(state, lot = DEFAULT_LOT, random = Math.random) {
  if (state.bankrupt) return state
  state.tick += 1
  const previousPrice = state.price
  const drift = Math.sin(state.tick / 18) * 0.32
  state.price = round(Math.max(100, previousPrice + drift + (random() - 0.5) * 1.5))
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
    const reason = movement <= -STOP_DISTANCE ? '손절' : movement >= TARGET_DISTANCE ? '익절' : state.tick - position.openedAt >= 32 ? '시간 청산' : state.equity <= 0 ? '잔고 소진' : null
    if (reason) {
      state.balance = round(state.balance + pnl)
      state.tradeCount += 1
      state.trades.unshift({ ...position, id: state.tradeCount, exit: exitPrice(state.price, position.side), profit: pnl, reason })
      state.trades = state.trades.slice(0, 20)
      state.position = null
      state.cooldown = 4
      state.status = `${reason} 완료 · 다음 진입 대기`
      state.bankrupt = state.balance <= 0
    } else {
      state.status = `${position.side === 'BUY' ? '매수' : '매도'} 보유 중 · 익절/손절 감시`
    }
  } else if (state.cooldown > 0) {
    state.cooldown -= 1
  } else if (state.tick >= 4) {
    const closes = state.candles.map(candle => candle.close)
    const fast = average(closes.slice(-5))
    const slow = average(closes.slice(-12))
    if (Math.abs(fast - slow) >= 0.12) {
      const side = fast > slow ? 'BUY' : 'SELL'
      const entry = round(state.price + sideSign(side) * SPREAD / 2)
      const validLot = normalizeLot(lot)
      state.position = { side, entry, lot: validLot, openedAt: state.tick, candleId: state.candles[state.candles.length - 1].id, stop: round(entry - sideSign(side) * STOP_DISTANCE), target: round(entry + sideSign(side) * TARGET_DISTANCE) }
      state.status = `${side === 'BUY' ? '매수' : '매도'} 진입 · 이동평균 추세 감지`
    } else {
      state.status = '횡보 구간 · 추세 형성 대기'
    }
  }
  pnl = floatingProfit(state)
  state.equity = round(state.balance + pnl)
  state.peakEquity = Math.max(state.peakEquity, state.equity)
  state.maxDrawdown = Math.max(state.maxDrawdown, (state.peakEquity - state.equity) / state.peakEquity * 100)
  if (state.bankrupt) state.status = '가상 잔고 소진 · 다시 시작해 주세요'
  return state
}
