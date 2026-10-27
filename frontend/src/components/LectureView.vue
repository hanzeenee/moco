<template>
  <div class="lecture-page">
    <div class="lecture-layout">
      <div class="lecture-left">
        <div class="lecture-left-content">
          <div class="lecture-text">
            <div>MOCO - 해외선물 자동매매 MT5 EA</div>
            <div>Money Copier</div>
          </div>

          <button class="go-classroom-btn" type="button" @click="goToClassroom">
            강의실 바로가기
          </button>
        </div>
      </div>

      <div class="lecture-right">
        <div class="video-section">
          <iframe
            class="video-player"
            src="https://www.youtube.com/embed/mbQomARqpfo"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LectureView',

  methods: {
    goToClassroom() {
      this.$router.push('/classroom')
    }
  }
}
</script>

<style scoped>
.lecture-page {
  background: #000000;
  min-height: calc(100vh - 56px);
  padding: 30px;
  box-sizing: border-box;
}

.lecture-layout {
  display: flex;
  gap: 30px;
  align-items: center;
  min-height: calc(100vh - 116px);
}

.lecture-left,
.lecture-right {
  flex: 1;
}

.lecture-left {
  display: flex;
  justify-content: center;
  align-items: center;
}

.lecture-left-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}

.lecture-text {
  color: #ffffff;
  font-size: 40px;
  font-weight: bold;
  line-height: 1.5;
  text-align: center;
}

.go-classroom-btn {
  padding: 12px 24px;
  border: 1px solid #ffffff;
  background: transparent;
  color: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
}

.go-classroom-btn:hover {
  background: #ffffff;
  color: #000000;
}

.video-section {
  width: 100%;
}

.video-player {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
}
</style>
