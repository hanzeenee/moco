<template>
  <section ref="simulator" class="simulator" aria-label="가상 EA 트레이딩 체험">
    <header class="sim-heading">
      <button class="exit-btn" type="button" @click="$emit('exit')">소개로 돌아가기 ↗</button>
    </header>

    <div class="terminal">
      <div class="terminal-title"><span class="terminal-icon"><img src="../assets/brand/moconix-mark-transparent.png" alt="" /></span><strong>MOCONIX Terminal</strong><span class="demo-badge">가상 체험</span></div>
      <div class="toolbar">
        <button class="reset-btn" type="button" @click="reset">↻ 다시 시작</button>
      </div>

      <div class="chart-heading"><strong>XAUUSD <span>· M{{ candleMinutes }}</span></strong><span v-if="state.eaApplied" class="ea-name">MOCONIX EA ☺</span><button v-else class="apply-ea-btn" type="button" @click="applyEa">EA 적용하기</button></div>
      <div class="quote-strip">
        <div class="quote sell"><span>SELL</span><strong>{{ (state.price - 0.1).toFixed(2) }}</strong></div>
        <label class="lot-control" for="simulation-lot">거래량<span class="lot-input"><input id="simulation-lot" v-model.number="lotInput" type="number" min="0.01" max="100" step="0.01" inputmode="decimal" aria-label="거래량 (랏)" title="0.01~100랏" @change="applyLot" @blur="applyLot" @keydown.enter="$event.target.blur()" /><span>랏</span></span></label>
        <div class="quote buy"><span>BUY</span><strong>{{ (state.price + 0.1).toFixed(2) }}</strong></div>
      </div>

      <div ref="chart" class="chart">
        <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" :style="{ height: chartHeight + 'px' }" role="img" aria-label="자동으로 움직이는 가상 금 시세 캔들 차트">
          <defs><clipPath id="ea-chart-clip"><rect x="0" y="8" :width="plotWidth" :height="chartHeight - 28" /></clipPath></defs>
          <g v-for="line in gridLines" :key="line.value" class="chart-grid"><line x1="0" :x2="plotWidth" :y1="line.y" :y2="line.y"/><text :x="plotWidth + 5" :y="line.y + 3">{{ line.value.toFixed(1) }}</text></g>
          <g clip-path="url(#ea-chart-clip)">
            <g v-for="candle in chartCandles" :key="candle.id" class="candle">
              <line :x1="candle.x" :x2="candle.x" :y1="priceY(candle.high)" :y2="priceY(candle.low)" />
              <rect :x="candle.x - candleWidth / 2" :y="priceY(Math.max(candle.open, candle.close))" :width="candleWidth" :height="Math.max(1, Math.abs(priceY(candle.open) - priceY(candle.close)))" :fill="candle.close >= candle.open ? '#050805' : '#62ff2b'" />
            </g>
            <g v-if="displayOrder" class="order-lines" :class="{ 'closed-order': !state.position }"><line x1="0" :x2="plotWidth" :y1="priceY(displayOrder.entry)" :y2="priceY(displayOrder.entry)" stroke="#ffffff"/><line x1="0" :x2="plotWidth" :y1="priceY(displayOrder.stop)" :y2="priceY(displayOrder.stop)" stroke="#ff858c"/><line x1="0" :x2="plotWidth" :y1="priceY(displayOrder.target)" :y2="priceY(displayOrder.target)" stroke="#79c2ff"/><text x="7" :y="priceY(displayOrder.target) - 5" fill="#79c2ff">TP</text><text x="7" :y="priceY(displayOrder.stop) - 5" fill="#ff858c">SL</text></g>
            <g v-for="marker in markers" :key="marker.key"><path :d="marker.path" :fill="marker.side === 'BUY' ? '#48aaff' : '#ff7b85'" /></g>
            <g v-for="marker in exitMarkers" :key="`exit-${marker.id}`" class="exit-marker"><circle :cx="marker.x" :cy="marker.y" r="3.5" :fill="marker.color" stroke="#000"/><text :x="marker.x - 6" :y="marker.y - 6" text-anchor="end" :fill="marker.color">{{ marker.label }}</text></g>
          </g>
          <line x1="0" :x2="plotWidth" :y1="priceY(state.price)" :y2="priceY(state.price)" stroke="#718491" stroke-width="0.7" />
          <rect :x="plotWidth" :y="priceY(state.price) - 8" width="46" height="16" fill="#173142"/><text :x="plotWidth + 4" :y="priceY(state.price) + 3" fill="#e3f2ff" class="axis-label">{{ state.price.toFixed(2) }}</text>
          <text x="6" :y="chartHeight - 8" class="time-label">{{ timeLabel(chartCandles[0]?.id) }}</text><text :x="plotWidth - 2" :y="chartHeight - 8" text-anchor="end" class="time-label">{{ timeLabel(state.candles[state.candles.length - 1].id) }}</text>
        </svg>
        <div v-if="state.bankrupt" class="end-overlay"><span>체험 종료</span></div>
      </div>

      <div class="ea-status"><span class="status-dot" :class="{ inactive: !state.eaApplied || state.bankrupt }"></span>{{ state.status }}</div>
      <div class="account-stats">
        <div><span>잔고</span><strong>${{ money(state.balance) }}</strong></div>
        <div><span>평가금</span><strong :class="profitClass(state.equity - 10000)">${{ money(state.equity) }}</strong></div>
        <div><span>최대 낙폭</span><strong>{{ state.maxDrawdown.toFixed(2) }}%</strong></div>
      </div>
      <div class="trade-panel">
        <div class="panel-tab"><span class="trade-label">거래 <span>{{ state.entryCount }}</span></span><span class="trade-counts"><span class="positive">익절 {{ state.winCount }}회</span><span class="negative">손절 {{ state.lossCount }}회</span></span></div>
        <div class="trade-scroll" tabindex="0" aria-label="현재 거래 내역">
          <table><thead><tr><th>종목 / 유형</th><th>거래량</th><th>진입가</th><th>SL</th><th>TP</th><th>현재가</th><th>손익</th></tr></thead><tbody><tr v-if="state.position"><td>XAUUSD <b :class="state.position.side.toLowerCase()">{{ state.position.side }}</b></td><td>{{ state.position.lot.toFixed(2) }}</td><td>{{ state.position.entry.toFixed(2) }}</td><td>{{ state.position.stop.toFixed(2) }}</td><td>{{ state.position.target.toFixed(2) }}</td><td>{{ state.price.toFixed(2) }}</td><td :class="profitClass(openProfit)">{{ signed(openProfit) }}</td></tr><tr v-else><td colspan="7" class="empty-position">{{ state.bankrupt ? '다시 시작하면 새 잔고로 체험할 수 있어요.' : state.eaApplied ? '다음 거래를 기다리고 있어요.' : 'EA 적용 후 거래가 시작돼요.' }}</td></tr></tbody></table>
        </div>
        <div class="last-trade">{{ lastTradeText }}</div>
      </div>
    </div>
  </section>
</template>

<script>
import { advanceSimulation, createSimulation, applyEa, floatingProfit, normalizeLot, DEFAULT_LOT, CANDLE_MINUTES, TICK_INTERVAL_MS } from '../lib/eaSimulation.mjs'

export default {
  name: 'EaSimulator',
  emits: ['exit'],
  data() {
    return { state: createSimulation(), lot: DEFAULT_LOT, lotInput: DEFAULT_LOT, candleMinutes: CANDLE_MINUTES, chartWidth: 560, chartHeight: 200 }
  },
  computed: {
    plotWidth() { return Math.max(80, this.chartWidth - 48) },
    chartCandles() {
      const count = this.chartWidth < 240 ? 22 : this.chartWidth < 400 ? 36 : 54
      const candles = this.state.candles.slice(-count)
      return candles.map((candle, i) => ({ ...candle, x: (i + 0.5) * this.plotWidth / candles.length }))
    },
    candleWidth() { return Math.max(1, this.plotWidth / this.chartCandles.length * 0.55) },
    priceRange() {
      const values = this.chartCandles.flatMap(c => [c.low, c.high])
      if (this.displayOrder) values.push(this.displayOrder.stop, this.displayOrder.target)
      const min = Math.min(...values), max = Math.max(...values)
      const pad = Math.max(1, (max - min) * 0.14)
      return { min: min - pad, max: max + pad }
    },
    gridLines() {
      return Array.from({ length: 5 }, (_, i) => {
        const value = this.priceRange.min + (this.priceRange.max - this.priceRange.min) * i / 4
        return { value, y: this.priceY(value) }
      })
    },
    markers() {
      const positions = [...this.state.trades, ...(this.state.position ? [this.state.position] : [])]
      return positions.flatMap(position => {
        const candle = this.chartCandles.find(c => c.id === position.candleId)
        if (!candle) return []
        const y = this.priceY(position.side === 'BUY' ? candle.low : candle.high)
        const direction = position.side === 'BUY' ? 1 : -1
        return [{ key: position.openedAt, side: position.side, path: `M ${candle.x} ${y + direction * 4} l -4 ${direction * 7} h 8 Z` }]
      })
    },
    displayOrder() { return this.state.position || (this.state.cooldown > 0 ? this.state.trades[0] : null) },
    exitMarkers() {
      return this.state.trades.flatMap(trade => {
        const candle = this.chartCandles.find(c => c.id === trade.exitCandleId)
        return candle ? [{ id: trade.id, x: candle.x, y: this.priceY(trade.exitMid), label: trade.exitTarget, color: trade.exitTarget === 'TP' ? '#79c2ff' : '#ff858c' }] : []
      })
    },
    openProfit() { return floatingProfit(this.state) },
    lastTradeText() {
      if (!this.state.eaApplied) return 'EA 적용 전 · 차트만 실행 중입니다.'
      const last = this.state.trades[0]
      return last ? `최근 청산 · ${last.side} ${last.lot.toFixed(2)} · ${last.reason} ${this.signed(last.profit)}` : '가상 EA가 매수·매도 포지션을 자동으로 실행합니다.'
    }
  },
  mounted() {
    this.resizeObserver = new ResizeObserver(() => {
      this.chartWidth = Math.max(128, Math.floor(this.$refs.chart.getBoundingClientRect().width))
      this.$nextTick(this.fitChartHeight)
    })
    this.resizeObserver.observe(this.$refs.chart)
    this.resizeObserver.observe(this.$refs.simulator)
    window.addEventListener('resize', this.fitChartHeight)
    this.$nextTick(this.fitChartHeight)
    this.tickTimer = window.setInterval(() => {
      if (!document.hidden) {
        advanceSimulation(this.state, this.lot)
      }
    }, TICK_INTERVAL_MS)
  },
  beforeUnmount() {
    window.clearInterval(this.tickTimer)
    this.resizeObserver.disconnect()
    window.removeEventListener('resize', this.fitChartHeight)
  },
  methods: {
    fitChartHeight() {
      const simulator = this.$refs.simulator
      const chart = this.$refs.chart
      if (!simulator || !chart) return
      const panel = simulator.parentElement
      const padding = window.getComputedStyle(panel)
      const fixedHeight = simulator.getBoundingClientRect().height - chart.getBoundingClientRect().height
      const available = window.innerHeight - panel.getBoundingClientRect().top - parseFloat(padding.paddingTop) - parseFloat(padding.paddingBottom)
      this.chartHeight = Math.max(100, Math.min(440, Math.floor(available - fixedHeight - 4)))
    },
    applyLot() { this.lot = normalizeLot(this.lotInput); this.lotInput = this.lot },
    applyEa() { this.applyLot(); applyEa(this.state) },
    reset() { this.state = createSimulation() },
    priceY(value) { return 14 + (this.priceRange.max - value) / (this.priceRange.max - this.priceRange.min) * (this.chartHeight - 54) },
    money(value) { return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) },
    signed(value) { return `${value >= 0 ? '+' : '−'}$${this.money(Math.abs(value))}` },
    profitClass(value) { return value > 0 ? 'positive' : value < 0 ? 'negative' : '' },
    timeLabel(id = 0) { return `${String((9 + Math.floor(id * CANDLE_MINUTES / 60)) % 24).padStart(2, '0')}:${String(id * CANDLE_MINUTES % 60).padStart(2, '0')}` }
  }
}
</script>

<style scoped>
.simulator { line-height: 1.35; width: 100%; max-width: 860px; min-width: 0; color: #d6dce4; text-align: left; font-family: Arial, 'Malgun Gothic', sans-serif; }
.sim-heading { display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
button, input { font: inherit; }
button { cursor: pointer; }
button:focus-visible, input:focus-visible, .trade-scroll:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
.exit-btn { padding: 6px 0; background: none; border: 0; color: #a1abb7; font-size: 15px; }
.exit-btn:hover { color: #fff; }
.terminal { overflow: hidden; border: 1px solid #37434b; background: #080b0d; box-shadow: 0 12px 36px #0006; }
.terminal-title { display: flex; align-items: center; gap: 8px; min-height: 28px; padding: 0 10px; background: #102b3b; font-size: 11px; flex-wrap: wrap; }
.terminal-icon { position: relative; display: inline-block; width: 28px; height: 14px; overflow: hidden; flex: 0 0 auto; }
.terminal-icon img { position: absolute; width: 228%; max-width: none; height: auto; left: -64%; top: 50%; transform: translateY(-50%); }
.demo-badge { margin-left: auto; color: #abbed0; font-size: 10px; }
.toolbar { display: flex; align-items: center; gap: 8px; padding: 4px 8px; border-bottom: 1px solid #34383d; background: #202226; flex-wrap: wrap; }
.toolbar button { border: 1px solid #525b64; border-radius: 2px; padding: 4px 8px; background: #262a30; color: #ccd3dc; font-size: 11px; }
.toolbar button:hover { filter: brightness(1.2); }
.status-dot { display: inline-block; width: 6px; height: 6px; margin-right: 6px; border-radius: 50%; background: #70ed98; flex: 0 0 auto; }
.status-dot.inactive { background: #7a8592; }
.reset-btn { margin-left: auto; }
.chart-heading { min-height: 38px; box-sizing: border-box; align-items: center; display: flex; justify-content: space-between; gap: 6px; padding: 7px 10px 3px; font-size: 10px; flex-wrap: wrap; }
.chart-heading strong { color: #e1e9f2; font-size: 11px; }
.chart-heading strong span { color: #8194a8; font-weight: 400; }
.ea-name { color: #9caebd; }
.apply-ea-btn { border: 1px solid #ffd000; background: #ffd000; color: #151515; border-radius: 3px; padding: 5px 9px; font-size: 11px; font-weight: 700; }
.apply-ea-btn:hover { background: #ffdf46; border-color: #ffdf46; }
.quote-strip { display: flex; gap: 2px; align-items: stretch; padding: 4px 10px 0; }
.quote { display: flex; flex-direction: column; min-width: 0; width: 96px; padding: 4px 7px; border: 1px solid #9e535b; background: linear-gradient(#78363e, #3b1b22); font-family: Consolas, monospace; }
.quote span { font-size: 9px; color: #bacde9; }
.quote strong { text-align: center; font-size: clamp(12px, 1.65vw, 21px); font-weight: 400; color: #fff; }
.quote.buy { background: linear-gradient(#183d75, #102342); border-color: #4776a9; }
.lot-control { display: flex; flex-direction: column; justify-content: center; gap: 4px; min-width: 0; padding: 0 5px; font-size: 9px; color: #aeb7c2; text-align: center; }
.lot-input { display: flex; align-items: center; gap: 3px; }
.lot-input > span { font-size: 10px; }
.lot-control input { text-align: center; width: 72px; min-width: 0; box-sizing: border-box; border: 1px solid #5b646d; color: #fff; background: #252a30; border-radius: 0; padding: 2px; font-size: 11px; }
.chart { position: relative; margin: 0 6px; background: #000; }
.chart svg { display: block; width: 100%; height: 224px; font-family: Consolas, monospace; }
.chart-grid line { stroke: #15221b; stroke-dasharray: 2 5; stroke-width: 0.6; }
.chart-grid text, .time-label { fill: #8f9b9f; font-size: 9px; }
.axis-label { font-size: 9px; }
.candle { stroke: #62ff2b; stroke-width: 1; }
.order-lines line { stroke-dasharray: 4 4; stroke-width: 0.8; }
.order-lines text { font-size: 9px; }
.closed-order { opacity: 0.65; }
.exit-marker text { font: 9px Consolas, monospace; paint-order: stroke; stroke: #000; stroke-width: 3px; }
.end-overlay { position: absolute; inset: 0; display: grid; place-items: center; background: #0005; pointer-events: none; }
.end-overlay span { background: #18222ee6; padding: 9px 15px; border: 1px solid #506173; color: #e9edf3; font-size: 13px; }
.ea-status { display: flex; align-items: center; min-height: 28px; padding: 6px 10px; box-sizing: border-box; background: #101a16; border-top: 1px solid #273d30; font-size: 10px; color: #a8c5b1; line-height: 1.5; }
.account-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; padding: 9px 10px; background: #1c2025; }
.account-stats > div { min-width: 0; }
.account-stats span { display: block; margin-bottom: 5px; color: #9ba5b2; font-size: 10px; }
.account-stats strong { font-family: Consolas, monospace; font-size: clamp(11px, 1.3vw, 17px); font-weight: 400; overflow-wrap: anywhere; }
.positive { color: #79c2ff; }
.negative { color: #ff858c; }
.trade-panel { background: #16191d; }
.panel-tab { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 6px; padding: 7px 10px; border-top: 1px solid #3a4048; border-bottom: 1px solid #343a43; font-size: 11px; }
.trade-label { white-space: nowrap; }
.trade-label > span { color: #98a9b9; }
.trade-counts { grid-column: 2; display: flex; justify-content: center; gap: 10px; font-size: 10px; white-space: nowrap; }
.trade-scroll { width: 100%; overflow-x: auto; }
table { width: 100%; min-width: 500px; border-collapse: collapse; white-space: nowrap; font-family: Consolas, 'Malgun Gothic', monospace; font-size: 10px; }
th, td { text-align: right; padding: 6px 8px; font-weight: 400; }
tbody tr { height: 34px; }
th { color: #8896a3; background: #1c2025; }
th:first-child, td:first-child { text-align: left; }
td b { font-size: 9px; padding-left: 3px; font-weight: 400; }
td .buy { color: #79c2ff; } td .sell { color: #ff858c; }
.empty-position { height: 22px; color: #85929e; }
.last-trade { min-height: 28px; box-sizing: border-box; padding: 7px 10px; border-top: 1px solid #2c323a; color: #9ba6b2; font-size: 10px; line-height: 1.5; }
@media (max-width: 600px) {
  .panel-tab { grid-template-columns: minmax(0, 1fr); }
  .trade-counts { grid-column: 1; gap: 8px; }
  .sim-heading { gap: 5px; margin-bottom: 12px; }
  .exit-btn { font-size: 13px; }
  .terminal-title { padding: 6px; gap: 4px; }
  .terminal-title strong { font-size: 10px; }
  .demo-badge { margin-left: 0; }
  .toolbar { padding: 6px; gap: 5px; }
  .toolbar button { padding: 5px; font-size: 10px; }
  .reset-btn { margin-left: 0; }
  .chart-heading { padding: 8px 6px 4px; }
  .quote-strip { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 4px; padding: 4px 5px 0; }
  .quote { width: auto; padding: 4px; }
  .quote.sell { grid-row: 1; grid-column: 1; }
  .quote.buy { grid-row: 1; grid-column: 2; }
  .lot-control { grid-row: 2; grid-column: 1 / -1; flex-direction: row; align-items: center; gap: 6px; padding: 2px 0; font-size: 10px; }
  .lot-control input { text-align: center; width: 72px; flex: 0 0 72px; font-size: 11px; }
  .chart { margin: 0 3px; }
  .account-stats { gap: 9px; padding: 10px 6px; grid-template-columns: 1fr; }
  .account-stats > div { display: flex; justify-content: space-between; align-items: center; }
  .account-stats span { margin: 0; }
  .ea-status { padding: 6px; }
}
</style>
