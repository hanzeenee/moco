<template>
  <div class="classroom-page">
    <div class="top-section">
      <div class="classroom-layout">
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
          @click="changeToCommentTab"
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

        <div v-else-if="activeTab === 'comment'" class="comment-box">
          <div class="content-title">댓글</div>

          <div class="comment-list">
            <div
              v-for="comment in comments"
              :key="comment.id"
              class="comment-item"
            >
              <div class="comment-header">
                <span class="comment-author">{{ comment.author_name }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>

              <div class="comment-body">
                {{ comment.content }}
              </div>
            </div>

            <div v-if="comments.length === 0" class="empty-comment">
              아직 댓글이 없습니다.
            </div>
          </div>

          <div class="comment-input-wrap">
            <textarea
              v-model="newComment"
              class="comment-textarea"
              placeholder="댓글을 입력하세요."
            ></textarea>

            <div class="comment-action">
              <button class="comment-submit-btn" @click="submitComment">
                입력
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ClassroomView',

  data() {
    return {
      activeTab: 'material',
      newComment: '',
      comments: [],

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

  mounted() {
    this.loadComments()
  },

  methods: {
    getCookie(name) {
      const value = `; ${document.cookie}`
      const parts = value.split(`; ${name}=`)
      if (parts.length === 2) {
        return parts.pop().split(';').shift()
      }
      return null
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return dateString.replace('T', ' ').slice(0, 16)
    },

    async loadComments() {
      const url = `/api/comments/?lecture_id=${this.currentLecture.id}`
      console.log('댓글 조회 URL:', url)

      try {
        const response = await axios.get(url)
        console.log('댓글 조회 응답:', response.data)
        this.comments = response.data
      } catch (error) {
        console.error('댓글 조회 실패:', error)
      }
    },

    async selectLecture(lecture) {
      this.currentLecture = lecture
      this.activeTab = 'material'
      this.newComment = ''
      await this.loadComments()
    },

    async changeToCommentTab() {
      this.activeTab = 'comment'
      await this.loadComments()
    },

    async submitComment() {
      const content = this.newComment.trim()

      if (!content) {
        return
      }

      const url = '/api/comments/'
      const payload = {
        lecture_id: this.currentLecture.id,
        author_name: '한진희님',
        content: content
      }

      const csrfToken = this.getCookie('csrftoken')

      console.log('댓글 작성 URL:', url)
      console.log('댓글 작성 payload:', payload)
      console.log('CSRF Token:', csrfToken)

      try {
        const response = await axios.post(url, payload, {
          headers: {
            'X-CSRFToken': csrfToken
          }
        })

        console.log('댓글 작성 응답:', response.data)

        this.newComment = ''
        this.activeTab = 'comment'
        await this.loadComments()
      } catch (error) {
        console.error('댓글 작성 실패:', error)
      }
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

.comment-box {
  min-height: 260px;
}

.comment-list {
  margin-bottom: 20px;
}

.comment-item {
  background: #1a1a1a;
  border: 1px solid #333333;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 12px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
}

.comment-date {
  color: #999999;
  font-size: 12px;
}

.comment-body {
  color: #dddddd;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.empty-comment {
  color: #888888;
  font-size: 14px;
  padding: 20px 0;
}

.comment-input-wrap {
  border: 1px solid #333333;
  border-radius: 12px;
  background: #1a1a1a;
  padding: 14px;
  box-sizing: border-box;
}

.comment-textarea {
  width: 100%;
  min-height: 120px;
  resize: vertical;
  border: none;
  outline: none;
  background: transparent;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
  box-sizing: border-box;
}

.comment-textarea::placeholder {
  color: #888888;
}

.comment-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.comment-submit-btn {
  padding: 10px 18px;
  border: 1px solid #ffffff;
  background: transparent;
  color: #ffffff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
}

.comment-submit-btn:hover {
  background: #ffffff;
  color: #000000;
}

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

  .comment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>