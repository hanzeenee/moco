<template>
  <div class="main-area">
    <div class="main-panel main-panel-left" :class="{ 'game-open': gameOpen }">
      <EaSimulator v-if="gameOpen" @exit="gameOpen = false" />
      <div v-else class="main-content">
        <div class="intro-brand">
          <span class="intro-mark" aria-hidden="true"><img src="../assets/brand/moconix-mark-transparent.png" alt="" /></span>
          <p class="intro-eyebrow"><strong>MOCONIX</strong> | MT5 · TradingView 맞춤 개발</p>
        </div>

        <h1 class="intro-title">
          <span class="intro-lead">원하는 매매 전략과 기능을 그대로 구현하는,</span>
          <span class="intro-main">MT5 EA·인디케이터 및 TradingView 지표 개발 서비스</span>
        </h1>

        <p class="intro-services">신규 개발 · 기존 프로그램 수정 및 개선</p>
        <button class="game-start-btn" type="button" aria-label="EA 체험하기" @click="gameOpen = true"><img class="game-start-art game-start-frame" src="../assets/brand/ea-experience-button.png" alt="" aria-hidden="true" /><img class="game-start-art game-start-content" src="../assets/brand/ea-experience-button.png" alt="" aria-hidden="true" /></button>
      </div>
    </div>

    <div class="main-panel main-panel-right"><ServiceMenu /></div>
  </div>
</template>

<script>
import EaSimulator from './EaSimulator.vue'
import ServiceMenu from './ServiceMenu.vue'

export default {
  name: 'HomeView',
  components: { EaSimulator, ServiceMenu },
  data() { return { gameOpen: false } }
}
</script>

<style scoped>
.main-area { flex: 1; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: center; gap: var(--page-gap); width: 100%; max-width: var(--page-width); min-width: 0; margin: 0 auto; padding: clamp(24px, 4vh, 44px) var(--page-gutter) clamp(32px, 5vh, 56px); box-sizing: border-box; background: #000; }
.main-panel { display: flex; justify-content: center; align-items: center; min-width: 0; }
.main-content { display: flex; flex-direction: column; align-items: flex-start; width: 100%; max-width: var(--content-width); text-align: left; word-break: keep-all; overflow-wrap: anywhere; }
.intro-brand { display: flex; align-items: center; gap: 14px; max-width: 100%; margin-bottom: 30px; }
.intro-mark { position: relative; display: block; width: 38px; height: 20px; overflow: hidden; flex: 0 0 auto; }
.intro-mark img { position: absolute; width: 228%; max-width: none; height: auto; left: -64%; top: 50%; transform: translateY(-50%); }
.intro-eyebrow { margin: 0; color: #959ca8; font-size: 12px; font-weight: 500; line-height: 1.7; letter-spacing: .015em; }
.intro-eyebrow strong { color: #e3e5ea; font-weight: 700; letter-spacing: .06em; }
.intro-title { margin: 0; color: #f5f6f8; font-size: clamp(28px, 2.6vw, 40px); font-weight: 700; line-height: 1.42; letter-spacing: -.035em; }
.intro-title > span { display: block; text-wrap: balance; }
.intro-lead { color: #b5bbc5; font-size: clamp(16px, 1.45vw, 20px); font-weight: 500; line-height: 1.75; letter-spacing: -.02em; }
.intro-main { margin-top: 14px; }
.intro-services { margin: 26px 0 0; color: #959ca8; font-size: 14px; line-height: 1.8; letter-spacing: -.01em; }
.game-start-btn { position: relative; display: block; width: 240px; max-width: 100%; aspect-ratio: 15 / 4; margin-top: 30px; padding: 0; border: 0; border-radius: 999px; background: transparent; cursor: pointer; transform-origin: center; transition: transform .2s ease; }
/* Keep the supplied lettering and artwork unchanged; frame the original glow margins. */
.game-start-art { position: absolute; display: block; top: -25%; left: -4.166667%; width: 111.666667%; max-width: none; height: auto; pointer-events: none; transition: filter .2s ease; }
/* The unchanged 268x88 image supplies both layers. Separate its center from the rim. */
.game-start-frame { mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='268' height='88' viewBox='0 0 268 88'%3E%3Cdefs%3E%3Cfilter id='soft'%3E%3CfeGaussianBlur stdDeviation='2'/%3E%3C/filter%3E%3Cmask id='rim'%3E%3Crect width='268' height='88' fill='white'/%3E%3Crect x='51' y='23' width='183' height='52' rx='3' fill='black' filter='url(%23soft)'/%3E%3C/mask%3E%3C/defs%3E%3Crect width='268' height='88' fill='white' mask='url(%23rim)'/%3E%3C/svg%3E"); mask-size: 100% 100%; }
/* Keep the full pointer through source y71; fade only its outer glow through y74. Centering stays unchanged. */
.game-start-content { clip-path: inset(29.545455% 14.925373% 15.909091% 20.149254%); transform: translateX(-4.664179%); mix-blend-mode: screen; mask-image: linear-gradient(to right, transparent 20.149254%, #000 21.268657%, #000 83.955224%, transparent 85.074627%), linear-gradient(to bottom, transparent 29.545455%, #000 32.954545%, #000 80.681818%, transparent 84.090909%); mask-composite: intersect; }
@media (hover: hover) {
  .game-start-btn:hover { transform: scale(1.045); }
  .game-start-btn:hover .game-start-art { filter: brightness(1.25); }
}
.game-start-btn:active { transform: scale(.985); }
.game-start-btn:focus-visible { outline: 2px solid #fff; outline-offset: 6px; }
.game-start-btn:focus-visible .game-start-art { filter: brightness(1.25); }
@media (min-width: 981px) {
  /* Keep the grid anchored by the service list while only the left content changes. */
  .main-panel-left.game-open { position: relative; align-self: stretch; }
  .main-panel-left.game-open > :deep(.simulator) { position: absolute; top: 0; left: 0; }
}
@media (max-width: 980px) {
  .main-area { grid-template-columns: minmax(0, 1fr); gap: 40px; max-width: 720px; padding-top: 32px; padding-bottom: 48px; }
  .main-panel-left:not(.game-open) { min-height: 360px; padding: 12px 0; }
}
@media (max-width: 600px) {
  .main-area { gap: 28px; padding-top: 28px; padding-bottom: 40px; }
  .main-panel-left:not(.game-open) { min-height: 350px; }
  .intro-brand { gap: 12px; margin-bottom: 24px; }
  .intro-mark { width: 32px; height: 18px; }
  .intro-eyebrow { font-size: 11px; }
  .intro-title { font-size: 27px; }
  .intro-services { margin-top: 22px; font-size: 13px; }
  .game-start-btn { width: 224px; margin-top: 26px; }
}
@media (prefers-reduced-motion: reduce) { .game-start-btn, .game-start-art { transition: none; } .game-start-btn:hover, .game-start-btn:active { transform: none; } }
</style>
