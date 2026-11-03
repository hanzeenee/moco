<template>
  <form class="utility-login" @submit.prevent="submit">
    <p>{{ $t('등록된 인피녹스 계좌번호로 고객 전용 자료실에 로그인해 주세요.') }}</p>
    <label for="utility-account-number">{{ $t('인피녹스 계좌번호') }}</label>
    <input id="utility-account-number" v-model="accountNumber" type="text" inputmode="numeric" pattern="[0-9]{1,20}" maxlength="20" autocomplete="off" :placeholder="$t('계좌번호 입력')" required :disabled="pending" :aria-invalid="Boolean(error)" :aria-describedby="error ? 'utility-login-error' : 'utility-login-note'" />
    <p id="utility-login-note" class="login-note">{{ $t('자료실은 계좌 등록이 확인된 고객만 이용할 수 있습니다.') }}</p>
    <p v-if="error" id="utility-login-error" class="login-error" role="alert">{{ $t(error) }}<span v-if="registrationIssue" class="login-next-step">{{ $t('계좌 등록 여부를 아래 상담 채널로 문의해 주세요.') }}</span></p>
    <button class="utility-login-submit" type="submit" :disabled="pending">{{ pending ? $t('계좌번호 확인 중…') : $t('로그인') }}</button>
    <UtilityRegistrationHelp />
  </form>
</template>

<script>
import { csrfToken, utilityRequest } from '../lib/utilityAccess'
import UtilityRegistrationHelp from './UtilityRegistrationHelp.vue'

export default {
  name: 'UtilityAccountLogin',
  components: { UtilityRegistrationHelp },
  emits: ['authenticated'],
  data() { return { accountNumber: '', pending: false, error: '', registrationIssue: false } },
  methods: {
    async submit() {
      if (this.pending) return
      this.error = ''
      this.registrationIssue = false
      const account = this.accountNumber.trim()
      if (!/^[0-9]{1,20}$/.test(account)) { this.error = '계좌번호를 숫자로 입력해 주세요.'; return }
      this.pending = true
      try {
        await utilityRequest('session')
        await utilityRequest('login', {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
          body: JSON.stringify({ account_number: account }),
        })
        await this.$router.push('/utilities')
        this.accountNumber = ''
        this.$emit('authenticated')
      } catch (error) {
        this.registrationIssue = error.status === 403
        this.error = error.message || '네트워크 연결을 확인하고 다시 시도해 주세요.'
      } finally { this.pending = false }
    },
  },
}
</script>

<style scoped>
.utility-login { color: #bdc1c8; font-size: 14px; line-height: 1.8; }
.utility-login > p { margin: 0 0 18px; }
.utility-login label { display: block; margin-bottom: 7px; color: #e6e9ef; font-size: 13px; }
.utility-login input { width: 100%; box-sizing: border-box; padding: 12px 14px; border: 1px solid #505761; border-radius: 7px; background: #080a0c; color: #fff; font: inherit; font-size: 17px; letter-spacing: .04em; }
.utility-login input:focus { outline: 2px solid #ffd000; outline-offset: 2px; }
.utility-login .login-note { margin: 10px 0 18px; color: #8f98a7; font-size: 12px; }
.utility-login .login-error { margin: 0 0 14px; color: #ff959a; font-size: 13px; }
.login-next-step { display: block; margin-top: 5px; color: #aeb8c6; font-size: 12px; }
.utility-login-submit { width: 100%; min-height: 46px; padding: 10px 16px; border: 1px solid #ffd000; border-radius: 7px; background: #ffd000; color: #111; font: inherit; font-weight: 700; cursor: pointer; }
.utility-login-submit:hover { background: #ffdf46; }
.utility-login-submit:focus-visible { outline: 2px solid #fff; outline-offset: 3px; }
.utility-login-submit:disabled { opacity: .65; cursor: wait; }
</style>
