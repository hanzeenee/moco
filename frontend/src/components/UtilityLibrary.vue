<template>
  <section class="utility-library" aria-labelledby="utility-library-title">
    <div class="library-heading"><div><p class="library-eyebrow">{{ $t('MOCONIX · 등록 고객 전용') }}</p><h1 id="utility-library-title">{{ $t('EA·인디케이터 자료실') }}</h1></div><button v-if="authorized" type="button" :disabled="loggingOut" @click="logout">{{ $t('로그아웃') }}</button></div>
    <p v-if="authorized && !loading && libraryItems.length" class="library-intro">{{ $t('등록된 계좌로 로그인한 MT5에서만 실행됩니다.') }}</p>
    <div v-if="loading || !authorized || libraryItems.length === 0" class="library-empty" :class="{ 'library-waiting': authorized && !loading }" role="status">
      <template v-if="loading"><p>{{ $t('자료실 접속을 확인하고 있습니다.') }}</p></template>
      <template v-else-if="authorized"><span class="mdi mdi-file-outline" aria-hidden="true"></span><h2>{{ $t('자료를 준비하고 있습니다') }}</h2><p>{{ $t('EA와 인디케이터가 등록되면 이곳에서 다운로드할 수 있습니다.') }}</p></template>
      <template v-else><h2>{{ $t('자료실에 접속할 수 없습니다') }}</h2><p>{{ $t(error) }}</p><a href="/">{{ $t('홈으로 돌아가기') }}</a></template>
    </div>
    <section v-if="authorized && !loading && libraryItems.length" class="library-downloads" :aria-label="$t('다운로드 파일')">
      <div class="library-filters" role="group" :aria-label="$t('프로그램 종류')">
        <button v-for="category in categories" :key="category.value" type="button" :aria-pressed="selectedType === category.value" @click="selectedType = category.value">
          {{ $t(category.label) }}<span class="filter-count">{{ category.count }}</span>
        </button>
      </div>
      <div v-if="filteredItems.length" class="download-grid">
        <article v-for="item in filteredItems" :key="item.id" class="resource-card">
          <div class="resource-meta"><div class="resource-type"><span :class="['mdi', item.type === 'ea' ? 'mdi-robot' : 'mdi-chart-line']" aria-hidden="true"></span>{{ $t(item.type === 'ea' ? 'EA' : '인디케이터') }}</div><span v-if="item.version" class="resource-version">v{{ item.version }}</span></div>
          <h2>{{ $t(item.title) }}</h2><p>{{ $t(item.description) }}</p>
          <p v-if="item.note" class="resource-note">{{ $t(item.note) }}</p>
          <code>{{ item.filename }}</code>
          <a :href="item.download_url" download><span class="mdi mdi-download" aria-hidden="true"></span>{{ $t('EX5 다운로드') }}</a>
        </article>
      </div>
      <p v-else class="category-empty" role="status">{{ $t('이 종류의 자료를 준비하고 있습니다.') }}</p>
    </section>
    <UtilityInstallGuide v-if="authorized && !loading" :auth-bridge="authBridge" />
    <p v-if="logoutError" class="logout-error" role="alert">{{ $t(logoutError) }}</p>
  </section>
</template>

<script>
import { csrfToken, utilityRequest } from '../lib/utilityAccess'
import UtilityInstallGuide from './UtilityInstallGuide.vue'

export default {
  name: 'UtilityLibrary',
  components: { UtilityInstallGuide },
  data() { return { loading: true, authorized: false, items: [], selectedType: 'all', error: '', loggingOut: false, logoutError: '' } },
  computed: {
    libraryItems() { return this.items.filter(item => item.type !== 'helper') },
    filteredItems() { return this.selectedType === 'all' ? this.libraryItems : this.libraryItems.filter(item => item.type === this.selectedType) },
    categories() { return [
      { value: 'all', label: '전체', count: this.libraryItems.length },
      { value: 'ea', label: 'EA', count: this.libraryItems.filter(item => item.type === 'ea').length },
      { value: 'indicator', label: '인디케이터', count: this.libraryItems.filter(item => item.type === 'indicator').length },
    ] },
    authBridge() { return this.items.find(item => item.id === 'auth-bridge') || null },
  },
  async mounted() {
    try { const data = await utilityRequest('library'); this.items = data.items || []; this.authorized = true }
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
.library-empty.library-waiting { min-height: 160px; padding: 25px 20px; }
.library-waiting > .mdi { margin-bottom: 10px; font-size: 28px; }
.library-waiting h2 { font-size: 18px; }
.library-intro { margin: 14px 0 0; color: #949eae; font-size: 13px; line-height: 1.7; }
.library-downloads { margin-top: 26px; }
.library-filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
.library-filters button { display: inline-flex; align-items: center; gap: 9px; min-height: 42px; padding: 9px 15px; border: 1px solid #30353d; border-radius: 8px; background: #0b0d10; color: #a4afbf; font: inherit; font-size: 13px; cursor: pointer; }
.library-filters button:hover { border-color: #8c7927; color: #f1d365; }
.library-filters button[aria-pressed="true"] { border-color: #b49b31; background: #201c0d; color: #f1d365; }
.library-filters button:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
.filter-count { display: inline-grid; place-items: center; min-width: 19px; height: 19px; padding: 0 3px; box-sizing: border-box; border-radius: 5px; background: #ffffff0b; font-size: 11px; }
.category-empty { padding: 40px 20px; border: 1px solid #2b3038; border-radius: 12px; color: #949eae; text-align: center; font-size: 14px; }
.resource-meta { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.resource-version { color: #8d98a8; font-size: 11px; }
.resource-card .resource-note { padding-top: 12px; border-top: 1px solid #252b33; color: #949eae; font-size: 12px; }
.download-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.resource-card { display: flex; flex-direction: column; min-width: 0; padding: 24px; border: 1px solid #343b45; border-radius: 13px; background: #0b0d10; }
.resource-type { display: flex; align-items: center; gap: 8px; color: #cbb65c; font-size: 12px; }
.resource-type .mdi { font-size: 21px; }
.resource-card h2 { margin: 14px 0 10px; color: #edf0f4; font-size: 20px; }
.resource-card p { margin: 0 0 16px; color: #a4afbf; font-size: 13px; line-height: 1.8; }
.resource-card code { margin: auto 0 18px; color: #7f8c9e; font-size: 12px; overflow-wrap: anywhere; }
.resource-card a { display: flex; justify-content: center; align-items: center; gap: 8px; min-height: 43px; padding: 9px 12px; border: 1px solid #71601e; border-radius: 7px; background: #211d0d; color: #f1d365; text-decoration: none; font-size: 13px; font-weight: 600; }
.resource-card a:hover { border-color: #d3b72d; background: #30290d; }
.resource-card a:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
@media (max-width: 600px) { .download-grid { grid-template-columns: minmax(0, 1fr); gap: 13px; } .resource-card { padding: 21px; } }
.logout-error { margin-top: 15px; color: #ff959a; font-size: 13px; }
@media (max-width: 600px) { .utility-library { padding-top: 32px; } .library-empty { min-height: 280px; } }
</style>
