<template>
  <div class="classroom-page">
    <!-- 상단 영역 -->
    <div class="top-section">
      <div class="classroom-layout">
        <!-- 좌측: 영상 -->
        <div class="video-panel">
          <div class="video-title">
            {{ currentLecture.title }}
          </div>

          <div class="video-wrapper">
            <iframe
              class="video-player"
              :src="currentLecture.videoUrl"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>

          <div class="video-description">
            {{ currentLecture.description }}
          </div>
        </div>

        <!-- 우측: 강의 목록 -->
        <div class="list-panel">
          <div class="list-title">강의 목록</div>

          <button
            v-for="lecture in lectures"
            :key="lecture.id"
            class="lecture-item"
            :class="{ active: currentLecture.id === lecture.id }"
            @click="selectLecture(lecture)"
          >
            <div class="lecture-item-title">{{ lecture.title }}</div>
            <div class="lecture-item-desc">{{ lecture.shortText }}</div>
          </button>
        </div>
      </div>
    </div>

    <!-- 하단 영역 -->
    <div class="bottom-section">
      <div class="bottom-tabs">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'material' }"
          @click="activeTab = 'material'"
        >
          강의자료
        </button>

        <button
          class="tab-btn"
          :class="{ active: activeTab === 'quiz' }"
          @click="activeTab = 'quiz'"
        >
          퀴즈
        </button>

        <button
          class="tab-btn"
          :class="{ active: activeTab === 'comment' }"
          @click="activeTab = 'comment'"
        >
          댓글
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'material'" class="content-box">
          <div class="content-title">강의자료</div>
          <div class="content-text">
            추후 강의 PDF, 이미지, 설명 자료 등을 이 영역에 넣으면 됩니다.
          </div>
        </div>

        <div v-else-if="activeTab === 'quiz'" class="content-box">
          <div class="content-title">퀴즈</div>
          <div class="content-text">
            추후 문제, 정답 선택, 제출 버튼 등을 이 영역에 넣으면 됩니다.
          </div>
        </div>

        <div v-else-if="activeTab === 'comment'" class="content-box">
          <div class="content-title">댓글</div>
          <div class="content-text">
            추후 댓글 목록, 작성창, 답글 기능 등을 이 영역에 넣으면 됩니다.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ClassroomView',

  data() {
    return {
      activeTab: 'material',

      lectures: [
        {
          id: 1,
          title: '1강. 모코 - 해외선물 자동매매 MT5 EA',
          shortText: '입문 강의',
          description: '강의 설명 영역입니다. 추후 실제 설명으로 교체하면 됩니다.',
          videoUrl: 'https://www.youtube.com/embed/mbQomARqpfo'
        },
        {
          id: 2,
          title: '2강. Money Copier 기초',
          shortText: '기초 강의',
          description: '추후 실제 강의 설명을 넣을 수 있습니다.',
          videoUrl: 'https://www.youtube.com/embed/mbQomARqpfo'
        },
        {
          id: 3,
          title: '3강. 실전 세팅 방법',
          shortText: '실전 강의',
          description: '현재는 임시 영상/임시 텍스트입니다.',
          videoUrl: 'https://www.youtube.com/embed/mbQomARqpfo'
        },
        {
          id: 4,
          title: '4강. 운용 팁',
          shortText: '응용 강의',
          description: '나중에 각 강의별 실제 영상 링크로 교체하면 됩니다.',
          videoUrl: 'https://www.youtube.com/embed/mbQomARqpfo'
        }
      ],

      currentLecture: {
        id: 1,
        title: '1강. 모코 - 해외선물 자동매매 MT5 EA',
        shortText: '입문 강의',
        description: '강의 설명 영역입니다. 추후 실제 설명으로 교체하면 됩니다.',
        videoUrl: 'https://www.youtube.com/embed/mbQomARqpfo'
      }
    }
  },

  methods: {
    selectLecture(lecture) {
      this.currentLecture = lecture
      this.activeTab = 'material'
    }
  }
}
</script>

<style scoped>
.classroom-page {
  background: #000000;
  min-height: calc(100vh - 56px);
  padding: 24px;
  box-sizing: border-box;
}

/* 상단 */
.top-section {
  margin-bottom: 28px;
}

.classroom-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.video-panel {
  flex: 2.3;
  min-width: 0;
}

.list-panel {
  flex: 1;
  min-width: 280px;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  padding: 18px;
  box-sizing: border-box;
}

.video-title {
  color: #ffffff;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 16px;
}

.video-wrapper {
  width: 100%;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: block;
}

.video-description {
  margin-top: 16px;
  color: #cccccc;
  font-size: 15px;
  line-height: 1.6;
}

.list-title {
  color: #ffffff;
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 14px;
}

.lecture-item {
  width: 100%;
  text-align: left;
  padding: 14px;
  margin-bottom: 12px;
  border: 1px solid #333333;
  background: #1a1a1a;
  color: #ffffff;
  border-radius: 10px;
  cursor: pointer;
  box-sizing: border-box;
}

.lecture-item:hover {
  background: #222222;
}

.lecture-item.active {
  border-color: #777777;
  background: #252525;
}

.lecture-item-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 6px;
}

.lecture-item-desc {
  font-size: 13px;
  color: #aaaaaa;
}

/* 하단 */
.bottom-section {
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  overflow: hidden;
}

.bottom-tabs {
  display: flex;
  border-bottom: 1px solid #333333;
}

.tab-btn {
  padding: 14px 22px;
  border: none;
  background: transparent;
  color: #cccccc;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
}

.tab-btn:hover {
  background: #1b1b1b;
  color: #ffffff;
}

.tab-btn.active {
  background: #222222;
  color: #ffffff;
}

.tab-content {
  padding: 22px;
}

.content-box {
  min-height: 180px;
}

.content-title {
  color: #ffffff;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 14px;
}

.content-text {
  color: #cccccc;
  font-size: 15px;
  line-height: 1.7;
}

/* 반응형 */
@media (max-width: 1100px) {
  .classroom-layout {
    flex-direction: column;
  }

  .video-panel,
  .list-panel {
    width: 100%;
  }

  .list-panel {
    min-width: auto;
  }

  .bottom-tabs {
    flex-wrap: wrap;
  }
}
</style>