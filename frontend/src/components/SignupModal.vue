<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <button class="close-btn" @click="$emit('close')">×</button>

      <h1 class="modal-title">회원가입</h1>

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

      <div class="form-row">
        <div class="form-group half">
          <label class="form-label">생년월일 6자리</label>
          <input
            v-model="birth"
            type="text"
            maxlength="6"
            class="form-input"
            placeholder="900101"
          />
        </div>

        <div class="form-group half">
          <label class="form-label">휴대폰번호</label>
          <input
            v-model="phone"
            type="text"
            class="form-input"
            placeholder="01012345678"
          />
        </div>
      </div>

      <button class="submit-btn" @click="handleSignup">
        회원가입
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignupModal',

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
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 420px;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  padding: 24px 22px;
  box-sizing: border-box;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 12px;
  border: none;
  background: transparent;
  color: #ffffff;
  font-size: 22px;
  cursor: pointer;
}

.modal-title {
  color: #ffffff;
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 20px 0;
}

.form-group {
  margin-bottom: 12px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.half {
  flex: 1;
}

.form-label {
  display: block;
  color: #ffffff;
  font-size: 13px;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  box-sizing: border-box;
  border: 1px solid #444444;
  border-radius: 8px;
  background: #1b1b1b;
  color: #ffffff;
  font-size: 14px;
  outline: none;
}

.form-input:focus {
  border-color: #777777;
}

.submit-btn {
  width: 100%;
  height: 42px;
  margin-top: 6px;
  border: none;
  border-radius: 8px;
  background: #ffffff;
  color: #000000;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.submit-btn:hover {
  opacity: 0.9;
}
</style>