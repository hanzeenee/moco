<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">로그인</h1>

      <div class="form-group">
        <label class="form-label">아이디</label>
        <input
          v-model="username"
          type="text"
          class="form-input"
          placeholder="아이디를 입력하세요"
        />
      </div>

      <div class="form-group">
        <label class="form-label">비밀번호</label>
        <input
          v-model="password"
          type="password"
          class="form-input"
          placeholder="비밀번호를 입력하세요"
        />
      </div>

      <button class="login-btn" @click="handleLogin">
        로그인
      </button>

      <p class="login-desc">
        아직은 화면 틀만 구성된 상태입니다.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',

  data() {
    return {
      username: '',
      password: '',
    }
  },

  methods: {
    handleLogin() {
      // 추후 Django 로그인 API 연동 예정
      alert(`로그인 시도\n아이디: ${this.username}`)
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 56px);
  background: #000000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  padding: 32px 28px;
  box-sizing: border-box;
}

.login-title {
  color: #ffffff;
  font-size: 32px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 28px 0;
}

.form-group {
  margin-bottom: 18px;
}

.form-label {
  display: block;
  color: #ffffff;
  font-size: 14px;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  height: 46px;
  padding: 0 14px;
  box-sizing: border-box;
  border: 1px solid #444444;
  border-radius: 8px;
  background: #1b1b1b;
  color: #ffffff;
  font-size: 15px;
  outline: none;
}

.form-input:focus {
  border-color: #777777;
}

.login-btn {
  width: 100%;
  height: 48px;
  margin-top: 8px;
  border: none;
  border-radius: 8px;
  background: #ffffff;
  color: #000000;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.login-btn:hover {
  opacity: 0.9;
}

.login-desc {
  margin-top: 18px;
  color: #aaaaaa;
  font-size: 13px;
  text-align: center;
}
</style>