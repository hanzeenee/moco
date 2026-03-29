<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <button class="close-btn" @click="$emit('close')">×</button>

      <h1 class="modal-title">로그인</h1>

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

      <button class="submit-btn" @click="handleLogin">
        로그인
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginModal',

  data() {
    return {
      username: '',
      password: '',
    }
  },

  methods: {
    handleLogin() {
      this.$emit('login-success', {
        name: '한진희님'
      })
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
  padding: 24px;
}

.modal-card {
  width: 100%;
  max-width: 420px;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 14px;
  padding: 32px 28px;
  box-sizing: border-box;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  border: none;
  background: transparent;
  color: #ffffff;
  font-size: 24px;
  cursor: pointer;
}

.modal-title {
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

.submit-btn {
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
</style>