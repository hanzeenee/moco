<template>
  <div class="main-area">
    <div class="main-panel main-panel-left" :class="{ 'game-open': gameOpen }">
      <EaSimulator v-if="gameOpen" @exit="gameOpen = false" />
      <div v-else class="main-content">
        <p class="intro-eyebrow">MOCONIX | MT5 · TradingView 맞춤 개발</p>

        <h1 class="intro-title">
          <span>원하는 매매 전략과 기능을 그대로 구현하는,</span>
          <span>MT5 EA·인디케이터 및 TradingView 지표 개발 서비스</span>
        </h1>

        <p class="intro-services">신규 개발 · 기존 프로그램 수정 및 개선</p>
        <button class="game-start-btn" type="button" @click="gameOpen = true">EA 체험하기</button>
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
  max-width: 560px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
  text-align: left;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.intro-eyebrow {
  margin: 0;
  color: #c7c7c7;
  font-size: clamp(12px, 1.1vw, 14px);
  font-weight: 600;
  line-height: 1.6;
  letter-spacing: 0.04em;
}

.intro-title {
  margin: 0;
  color: #ffffff;
  font-size: clamp(20px, 2.1vw, 32px);
  font-weight: 700;
  line-height: 1.35;
}

.intro-title > span {
  display: block;
  text-wrap: balance;
}

.intro-services {
  margin: 0;
  color: #a6a6a6;
  font-size: clamp(12px, 1.1vw, 14px);
  line-height: 1.6;
}

.game-start-btn {
  max-width: 100%;
  padding: 12px 24px;
  border: 1px solid #ffd000;
  background: #ffd000;
  color: #000000;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.5;
  white-space: normal;
  word-break: keep-all;
  border-radius: 8px;
  cursor: pointer;
}

.game-start-btn:hover {
  border-color: #ffdf46;
  background: #ffdf46;
}

.game-start-btn:focus-visible {
  outline: 2px solid #ffffff;
  outline-offset: 4px;
}

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

  .main-content {
    gap: 16px;
  }
  .game-start-btn {
    padding: 10px 12px;
    font-size: 14px;
  }
}
</style>
