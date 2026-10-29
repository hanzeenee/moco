<template>
  <div class="main-area" :class="{ 'experience-open': gameOpen }">
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
        <button class="game-start-btn" type="button" @click="gameOpen = true"><span>EA 체험하기</span><span class="game-start-icon mdi mdi-cursor-default-click-outline" aria-hidden="true"></span></button>
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
@font-face { font-family: 'Moconix Nexon Lv1'; src: url('../assets/fonts/NEXONLv1GothicLowBold.otf') format('opentype'); font-style: normal; font-weight: 700; font-display: swap; }
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
.game-start-btn { display: inline-flex; align-items: center; justify-content: center; gap: 18px; width: 240px; max-width: 100%; min-height: 60px; margin-top: 30px; padding: 12px 24px; border: 2px solid #ffe433; border-radius: 999px; background: #050500; color: #ffe433; box-shadow: 0 0 7px #ffdf0059, 0 0 18px #ffd00026, inset 0 0 10px #ffd0001f; font-family: 'Moconix Nexon Lv1', Arial, 'Malgun Gothic', sans-serif; font-size: 20px; font-weight: 700; line-height: 1.5; text-align: center; white-space: normal; word-break: keep-all; cursor: pointer; transform-origin: center; transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease, color .2s ease; }
.game-start-icon { display: grid; place-items: center; flex: 0 0 30px; font-size: 30px; line-height: 1; font-weight: 400; }
@media (hover: hover) {
  .game-start-btn:hover { transform: scale(1.045); border-color: #fff078; color: #fff078; box-shadow: 0 0 12px #ffe43399, 0 0 30px #ffd00059, inset 0 0 14px #ffd00026; }
}
.game-start-btn:active { transform: scale(.985); }
.game-start-btn:focus-visible { outline: 2px solid #fff; outline-offset: 6px; box-shadow: 0 0 12px #ffe43399, 0 0 30px #ffd00059, inset 0 0 14px #ffd00026; }
@media (min-width: 981px) {
  .main-area.experience-open { align-items: start; padding-top: 20px; padding-bottom: 0; }
  .experience-open .main-panel-left { padding-bottom: 16px; }
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
  .game-start-btn { width: 224px; margin-top: 26px; padding: 11px 20px; font-size: 18px; min-height: 56px; }
}
@media (prefers-reduced-motion: reduce) { .game-start-btn { transition: none; } .game-start-btn:hover, .game-start-btn:active { transform: none; } }
</style>
