<template>
  <div class="signup-page">
    <div class="signup-card">
      <h1 class="signup-title">회원가입</h1>

      <div class="form-group">
        <label class="form-label">이메일</label>
        <input
          v-model="email"
          type="email"
          class="form-input"
          placeholder="이메일을 입력하세요"
        />
      </div>

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

      <div class="form-group">
        <label class="form-label">비밀번호 확인</label>
        <input
          v-model="passwordConfirm"
          type="password"
          class="form-input"
          placeholder="비밀번호를 다시 입력하세요"
        />
      </div>

      <div class="form-group">
        <label class="form-label">이름</label>
        <input
          v-model="name"
          type="text"
          class="form-input"
          placeholder="이름을 입력하세요"
        />
      </div>

      <div class="form-group">
        <label class="form-label">생년월일 6자리</label>
        <input
          v-model="birth"
          type="text"
          maxlength="6"
          class="form-input"
          placeholder="예: 900101"
        />
      </div>

      <div class="form-group">
        <label class="form-label">휴대폰번호</label>
        <input
          v-model="phone"
          type="text"
          class="form-input"
          placeholder="휴대폰번호를 입력하세요"
        />
      </div>

      <button class="signup-btn" @click="handleSignup">
        회원가입
      </button>

      <p class="signup-desc">
        현재는 회원가입 화면 틀만 구성된 상태입니다.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignupView',

  data() {
    return {
      email: '',
      username: '',
      password: '',
      passwordConfirm: '',
      name: '',
      birth: '',
      phone: '',
    }
  },

  methods: {
    handleSignup() {
      alert('회원가입 화면 틀만 구성된 상태입니다.')
    }
  }
}
</script>

<style scoped>
.signup-page {
  min-height: calc(100vh - 56px);
  background: #000000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.signup-card {
  width: 100%;
  max-width: 460px;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  padding: 32px 28px;
  box-sizing: border-box;
}

.signup-title {
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

.signup-btn {
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

.signup-btn:hover {
  opacity: 0.9;
}

.signup-desc {
  margin-top: 18px;
  color: #aaaaaa;
  font-size: 13px;
  text-align: center;
}
</style>