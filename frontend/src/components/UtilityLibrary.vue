<template>
  <section class="utility-library" aria-labelledby="utility-library-title">
    <div class="library-heading"><div><p class="library-eyebrow">{{ $t('MOCONIX · 등록 고객 전용') }}</p><h1 id="utility-library-title">{{ $t('무료 유틸리티 지표') }}</h1></div><button v-if="authorized" type="button" :disabled="loggingOut" @click="logout">{{ $t('로그아웃') }}</button></div>
    <div class="library-empty" role="status">
      <template v-if="loading"><p>{{ $t('자료실 접속을 확인하고 있습니다.') }}</p></template>
      <template v-else-if="authorized"><span class="mdi mdi-file-outline" aria-hidden="true"></span><h2>{{ $t('자료를 준비하고 있습니다') }}</h2><p>{{ $t('유틸리티 지표가 준비되면 이곳에서 안내해 드립니다.') }}</p></template>
      <template v-else><h2>{{ $t('자료실에 접속할 수 없습니다') }}</h2><p>{{ $t(error) }}</p><a href="/">{{ $t('홈으로 돌아가기') }}</a></template>
    </div>
    <p v-if="logoutError" class="logout-error" role="alert">{{ $t(logoutError) }}</p>
  </section>
</template>

<script>
import { csrfToken, utilityRequest } from '../lib/utilityAccess'

export default {
  name: 'UtilityLibrary',
  data() { return { loading: true, authorized: false, error: '', loggingOut: false, logoutError: '' } },
  async mounted() {
    try { await utilityRequest('library'); this.authorized = true }
    catch (error) { this.error = error.status === 401 ? '홈 화면에서 등록된 계좌번호로 다시 로그인해 주세요.' : error.message }
    finally { this.loading = false }
  },
  methods: {
    async logout() {
      this.loggingOut = true
      this.logoutError = ''
      try { await utilityRequest('logout', { method: 'POST', headers: { 'X-CSRFToken': csrfToken() } }); this.authorized = false; await this.$router.replace('/') }
      catch (error) { this.logoutError = error.message; this.loggingOut = false }
    },
  },
}
</script>

<style scoped>
.utility-library { width: 100%; max-width: 1000px; margin: 0 auto; padding: 48px var(--page-gutter) 64px; box-sizing: border-box; color: #eef0f4; }
.library-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
.library-eyebrow { margin: 0 0 9px; color: #b6a65f; font-size: 12px; letter-spacing: .04em; }
.library-heading h1 { margin: 0; font-size: clamp(24px, 3vw, 32px); }
.library-heading button { padding: 8px 13px; border: 1px solid #3b424d; border-radius: 6px; color: #b5bdca; font: inherit; font-size: 13px; cursor: pointer; }
.library-heading button:focus-visible, .library-empty a:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
.library-empty { display: grid; place-items: center; align-content: center; min-height: 300px; margin-top: 30px; padding: 35px 20px; border: 1px solid #2b3038; border-radius: 14px; background: #0b0d10; text-align: center; }
.library-empty > .mdi { margin-bottom: 14px; color: #bda638; font-size: 36px; }
.library-empty h2 { margin: 0 0 10px; font-size: 20px; font-weight: 500; }
.library-empty p { margin: 0; color: #949eae; font-size: 14px; line-height: 1.8; }
.library-empty a { margin-top: 18px; color: #ffd000; }
.logout-error { margin-top: 15px; color: #ff959a; font-size: 13px; }
@media (max-width: 600px) { .utility-library { padding-top: 32px; } .library-empty { min-height: 280px; } }
</style>
