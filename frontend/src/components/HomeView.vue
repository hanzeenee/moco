<template>
  <div class="main-area">
    <div class="main-panel main-panel-left" :class="{ 'game-open': gameOpen }">
      <EaSimulator v-if="gameOpen" @exit="gameOpen = false" />
      <div v-else class="main-content">
        <p class="intro-eyebrow">MT5 · TradingView 맞춤 개발</p>

        <h1 class="intro-title">
          <span>매매 아이디어를,</span>
          <span>실제로 동작하는 <span class="intro-accent">프로그램으로.</span></span>
        </h1>

        <p class="intro-description">
          <span>MT5 EA와 인디케이터, TradingView 지표까지.</span>
          <span>원하는 매매 조건과 표시 기능을 구체화해 구현합니다.</span>
        </p>

        <p class="intro-services">기존 EA 수정 · 기능 추가</p>
        <button class="game-start-btn" type="button" @click="gameOpen = true">EA 체험하기</button>
      </div>
    </div>

    <div class="main-panel main-panel-right" aria-hidden="true"></div>
  </div>
</template>

<script>
import EaSimulator from './EaSimulator.vue'

export default {
  name: 'HomeView',
  components: { EaSimulator },
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
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  text-align: center;
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
  font-size: clamp(20px, 3vw, 44px);
  font-weight: 700;
  line-height: 1.35;
}

.intro-title > span,
.intro-description > span {
  display: block;
}

.intro-accent {
  color: #ffd000;
}

.intro-description {
  margin: 0;
  color: #b8bcc4;
  font-size: clamp(13px, 1.25vw, 17px);
  line-height: 1.8;
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
