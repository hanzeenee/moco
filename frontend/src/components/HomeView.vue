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
          <span class="intro-main"><span class="intro-highlight">MT5 EA·인디케이터</span> 및 TradingView 지표 개발 서비스</span>
        </h1>

        <p class="intro-services">신규 개발 · 기존 프로그램 수정 및 개선</p>
        <button class="game-start-btn" type="button" @click="gameOpen = true"><span>EA 체험하기</span><span class="game-start-arrow" aria-hidden="true">→</span></button>
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
.main-area {
  flex: 1;
  width: 100%;
  min-width: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  background: #000000;
}

.main-panel {
  min-width: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 24px;
  box-sizing: border-box;
}

.main-panel-left {
  border-right: 1px solid #333333;
}

.main-panel-left.game-open {
  padding: 16px;
}

.main-content {
  width: 100%;
  max-width: 520px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.intro-brand { display: flex; align-items: center; gap: 14px; max-width: 100%; margin-bottom: 28px; }
.intro-mark { position: relative; display: block; width: 38px; height: 20px; overflow: hidden; flex: 0 0 auto; }
.intro-mark img { position: absolute; width: 228%; max-width: none; height: auto; left: -64%; top: 50%; transform: translateY(-50%); }
.intro-eyebrow { margin: 0; color: #959ca8; font-size: 12px; font-weight: 500; line-height: 1.7; letter-spacing: .015em; }
.intro-eyebrow strong { color: #e3e5ea; font-weight: 700; letter-spacing: .06em; }

.intro-title { margin: 0; color: #f5f6f8; font-size: clamp(26px, 2.5vw, 38px); font-weight: 700; line-height: 1.4; letter-spacing: -.035em; }
.intro-title > span { display: block; text-wrap: balance; }
.intro-lead { color: #b5bbc5; font-size: clamp(16px, 1.5vw, 20px); font-weight: 500; line-height: 1.75; letter-spacing: -.02em; }
.intro-main { margin-top: 12px; }
.intro-highlight { color: #ffd000; }
.intro-services { margin: 24px 0 0; color: #959ca8; font-size: 14px; line-height: 1.8; letter-spacing: -.01em; }

.game-start-btn { display: inline-flex; align-items: center; justify-content: space-between; gap: 30px; max-width: 100%; min-height: 52px; margin-top: 28px; padding: 12px 20px; border: 1px solid #ffd000; border-radius: 10px; background: #ffd000; color: #111; font: inherit; font-size: 15px; font-weight: 700; line-height: 1.5; text-align: left; white-space: normal; word-break: keep-all; cursor: pointer; transition: background .16s, border-color .16s, transform .16s; }
.game-start-arrow { font-size: 22px; font-weight: 400; line-height: 1; }
.game-start-btn:hover { border-color: #ffdf46; background: #ffdf46; transform: translateY(-1px); }
.game-start-btn:focus-visible { outline: 2px solid #fff; outline-offset: 4px; }
@media (prefers-reduced-motion: reduce) { .game-start-btn { transition: none; } .game-start-btn:hover { transform: none; } }
@media (max-width: 800px) {
  .main-area { grid-template-columns: minmax(0, 1fr); }
  .main-panel-left { border-right: 0; border-bottom: 1px solid #333333; }
  .main-panel-left:not(.game-open) { min-height: 460px; }
  .main-panel-right { padding: 36px 24px 48px; }
}

@media (max-width: 600px) {
  .main-panel-left.game-open { padding: 20px 8px; }

  .main-panel {
    padding: 24px 12px;
  }

  .main-panel-left:not(.game-open) { padding: 36px 24px; }
  .intro-brand { gap: 12px; margin-bottom: 22px; }
  .intro-mark { width: 32px; height: 18px; }
  .intro-eyebrow { font-size: 11px; }
  .intro-services { margin-top: 20px; font-size: 13px; }
  .game-start-btn {
    padding: 12px 18px;
    font-size: 14px;
  }
}
</style>
