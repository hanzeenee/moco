<template>
  <v-app>
    <TopBar />

    <v-main class="main-area">
      <div class="main-content">
        <div class="main-text">
          모코 - 해외선물 자동매매 MT5 EA<br>
          Money Copier
        </div>

        <button class="detail-btn" @click="goToLecture">
          강의 자세히보기
        </button>
      </div>
    </v-main>
  </v-app>
</template>

<script>
import TopBar from './components/TopBar.vue'

export default {
  name: 'App',

  components: {
    TopBar
  },

  methods: {
    goToLecture() {
      window.open("https://news.naver.com/", "_blank", "noopener,noreferrer");
    }
  }
}
</script>

<style>
.main-area {
  background: #000000;
  min-height: calc(100vh - 56px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.main-text {
  font-size: 40px;
  font-weight: bold;
  color: #ffffff;
  text-align: center;
}

.detail-btn {
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
</style>