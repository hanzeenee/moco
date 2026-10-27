<template>
  <div class="main-area">
    <div class="main-panel main-panel-left">
      <div class="main-content">
        <div class="main-text">
          MOCO - 해외선물 자동매매 MT5 EA<br>
          Money Copier
        </div>

        <button class="detail-btn" type="button" @click="goToLecture">
          강의 자세히 보기
        </button>
      </div>
    </div>

    <div class="main-panel main-panel-right" aria-hidden="true"></div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    goToLecture() {
      this.$router.push('/lecture')
    }
  }
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
  padding: 32px 24px;
  box-sizing: border-box;
}

.main-panel-left {
  border-right: 1px solid #333333;
}

.main-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.main-text {
  font-size: clamp(18px, 2.8vw, 40px);
  font-weight: bold;
  color: #ffffff;
  text-align: center;
  word-break: keep-all;
  overflow-wrap: anywhere;
}

.detail-btn {
  max-width: 100%;
  padding: 12px 24px;
  border: 1px solid #ffffff;
  background: transparent;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
}

.detail-btn:hover {
  background: #ffffff;
  color: #000000;
}

@media (max-width: 600px) {
  .main-panel {
    padding: 24px 12px;
  }

  .detail-btn {
    padding: 10px 12px;
    font-size: 14px;
  }
}
</style>
