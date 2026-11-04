<template>
  <section class="utility-library" aria-labelledby="utility-library-title">
    <div class="library-heading"><div><p class="library-eyebrow">{{ $t('MOCONIX · 등록 고객 전용') }}</p><h1 id="utility-library-title">{{ $t('EX5 자료실') }}</h1></div></div>
    <p v-if="authorized && !loading && libraryItems.length" class="library-intro">{{ $t('등록된 계좌로 로그인한 MT5에서만 실행됩니다.') }}</p>
    <div v-if="loading || !authorized || libraryItems.length === 0" class="library-empty" :class="{ 'library-waiting': authorized && !loading }" role="status">
      <template v-if="loading"><p>{{ $t('자료실 접속을 확인하고 있습니다.') }}</p></template>
      <template v-else-if="authorized"><span class="mdi mdi-file-outline" aria-hidden="true"></span><h2>{{ $t('자료를 준비하고 있습니다') }}</h2><p>{{ $t('EA와 인디케이터가 등록되면 이곳에서 다운로드할 수 있습니다.') }}</p></template>
      <template v-else><h2>{{ $t('자료실에 접속할 수 없습니다') }}</h2><p>{{ $t(error) }}</p><a href="/">{{ $t('홈으로 돌아가기') }}</a></template>
    </div>
    <section v-if="authorized && !loading && libraryItems.length" class="library-downloads" :aria-label="$t('다운로드 파일')">
      <div class="library-toolbar">
      <div v-if="!hasSearch" class="library-filters" role="group" :aria-label="$t('프로그램 종류')">
        <button v-for="category in categories" :key="category.value" type="button" :aria-pressed="selectedType === category.value" @click="selectCategory(category.value)">
          {{ $t(category.label) }}<span class="filter-count">{{ category.count }}</span>
        </button>
      </div>
      <span v-if="hasSearch" class="search-scope">{{ $t('EA·인디케이터 전체 검색') }}</span>
      <div class="library-search" role="search" :aria-label="$t('자료실 검색')">
        <span class="mdi mdi-magnify" aria-hidden="true"></span>
        <input v-model="searchQuery" type="search" :aria-label="$t('제목 또는 설명 검색')" :placeholder="$t('제목 또는 설명 검색')" autocomplete="off" />
        <button v-if="searchQuery" type="button" :aria-label="$t('검색어 지우기')" @click="searchQuery = ''"><span class="mdi mdi-close" aria-hidden="true"></span></button>
      </div>
      </div>
      <p v-if="hasSearch" class="search-result" role="status">{{ $t('검색 결과 {count}개', { count: filteredItems.length }) }}</p>
      <div v-if="filteredItems.length" class="download-grid">
        <article v-for="item in pagedItems" :key="item.id" class="resource-card">
          <div class="resource-meta"><div class="resource-type"><span :class="['mdi', item.type === 'ea' ? 'mdi-robot' : 'mdi-chart-line']" aria-hidden="true"></span>{{ $t(item.type === 'ea' ? 'EA' : '인디케이터') }}</div></div>
          <h2>{{ $t(item.title) }}</h2><p class="resource-description">{{ $t(item.description) }}</p>
          <a :href="item.download_url" download :aria-busy="downloadingId === item.id" :aria-disabled="downloadingId === item.id" @click.prevent="download(item)"><span class="mdi mdi-download" aria-hidden="true"></span>{{ $t('EX5 다운로드') }}</a>
        </article>
      </div>
      <nav v-if="pageCount > 1" class="library-pagination" :aria-label="$t('자료실 페이지')">
        <button type="button" :disabled="activePage === 1" :aria-label="$t('이전 페이지')" @click="changePage(activePage - 1)"><span class="mdi mdi-chevron-left" aria-hidden="true"></span></button>
        <template v-for="(page, index) in pageLinks" :key="index">
          <span v-if="page === null" class="page-ellipsis" aria-hidden="true">…</span>
          <button v-else type="button" :aria-label="$t('{page}페이지', { page })" :aria-current="page === activePage ? 'page' : undefined" @click="changePage(page)">{{ page }}</button>
        </template>
        <button type="button" :disabled="activePage === pageCount" :aria-label="$t('다음 페이지')" @click="changePage(activePage + 1)"><span class="mdi mdi-chevron-right" aria-hidden="true"></span></button>
      </nav>
      <p v-if="!filteredItems.length" class="category-empty" role="status">{{ $t(hasSearch ? '검색 결과가 없습니다. 다른 검색어를 입력해 주세요.' : '이 종류의 자료를 준비하고 있습니다.') }}</p>
    </section>
    <p v-if="downloadError" class="library-download-error" role="alert">{{ $t(downloadError) }}</p>
    <UtilityInstallGuide class="library-guide" v-if="authorized && !loading" v-model:selectedType="guideType" :auth-bridge="authBridge" @authorization-failed="denyAccess" />
  </section>
</template>

<script>
import { utilityRequest, downloadUtilityFile } from '../lib/utilityAccess'
import { libraryPage, libraryPageLinks } from '../lib/utilityLibrary.mjs'
import UtilityInstallGuide from './UtilityInstallGuide.vue'

export default {
  name: 'UtilityLibrary',
  components: { UtilityInstallGuide },
  data() { return { loading: true, authorized: false, items: [], selectedType: 'ea', guideType: 'ea', currentPage: 1, searchReturnPage: 1, searchQuery: '', error: '', downloadingId: '', downloadError: '', requestGeneration: 0 } },
  computed: {
    libraryItems() { return this.items.filter(item => item.type !== 'helper') },
    pageState() { return libraryPage(this.libraryItems, this.selectedType, this.currentPage, this.searchQuery, text => this.$t(text)) },
    hasSearch() { return this.searchQuery.trim().length > 0 },
    filteredItems() { return this.pageState.filteredItems },
    pagedItems() { return this.pageState.items },
    pageCount() { return this.pageState.pageCount },
    activePage() { return this.pageState.page },
    pageLinks() { return libraryPageLinks(this.activePage, this.pageCount) },
    categories() { return [
      { value: 'ea', label: 'EA', count: this.libraryItems.filter(item => item.type === 'ea').length },
      { value: 'indicator', label: '인디케이터', count: this.libraryItems.filter(item => item.type === 'indicator').length },
    ] },
    authBridge() { return this.items.find(item => item.id === 'auth-bridge') || null },
  },
  watch: {
    selectedType() { this.currentPage = 1 },
    searchQuery(value, previous) {
      const active = value.trim().length > 0
      const wasActive = previous.trim().length > 0
      if (!active && !wasActive) return
      if (active && !wasActive) this.searchReturnPage = this.currentPage
      this.currentPage = active ? 1 : this.searchReturnPage
    },
  },
  mounted() {
    this.loadLibrary()
    window.addEventListener('pageshow', this.restorePage)
  },
  beforeUnmount() {
    this.requestGeneration += 1
    window.removeEventListener('pageshow', this.restorePage)
  },
  methods: {
    async loadLibrary() {
      const generation = ++this.requestGeneration
      this.loading = true
      this.authorized = false
      this.items = []
      this.error = ''
      try {
        const data = await utilityRequest('library')
        if (generation !== this.requestGeneration) return
        this.items = data.items || []
        this.authorized = true
      } catch (error) {
        if (generation !== this.requestGeneration) return
        this.error = error.status === 401 ? '홈 화면에서 등록된 계좌번호로 다시 로그인해 주세요.' : error.message
      } finally { if (generation === this.requestGeneration) this.loading = false }
    },
    restorePage(event) { if (event.persisted) this.loadLibrary() },
    denyAccess(error) {
      this.requestGeneration += 1
      this.authorized = false
      this.items = []
      this.loading = false
      this.downloadError = ''
      this.error = error?.message || '홈 화면에서 등록된 계좌번호로 다시 로그인해 주세요.'
    },
    async download(item) {
      if (this.downloadingId) return
      this.downloadingId = item.id
      this.downloadError = ''
      try { await downloadUtilityFile(item.download_url, item.filename) }
      catch (error) {
        if (error.status === 401) this.denyAccess(error)
        else this.downloadError = error.message || '다운로드하지 못했습니다. 잠시 후 다시 시도해 주세요.'
      } finally { this.downloadingId = '' }
    },
    selectCategory(type) {
      this.selectedType = type
      this.guideType = type
    },
    changePage(page) { this.currentPage = page },
  },
}
</script>

<style scoped>
.utility-library { width: 100%; max-width: 1000px; margin: 0 auto; padding: 48px var(--page-gutter) 64px; box-sizing: border-box; color: #eef0f4; }
.library-heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
.library-eyebrow { margin: 0 0 9px; color: #b6a65f; font-size: 12px; letter-spacing: .04em; }
.library-heading h1 { margin: 0; font-size: clamp(24px, 3vw, 32px); }
.library-empty a:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
.library-empty { display: grid; place-items: center; align-content: center; min-height: 300px; margin-top: 30px; padding: 35px 20px; border: 1px solid #2b3038; border-radius: 14px; background: #0b0d10; text-align: center; }
.library-empty > .mdi { margin-bottom: 14px; color: #bda638; font-size: 36px; }
.library-empty h2 { margin: 0 0 10px; font-size: 20px; font-weight: 500; }
.library-empty p { margin: 0; color: #949eae; font-size: 14px; line-height: 1.8; }
.library-empty a { margin-top: 18px; color: #ffd000; }
.library-empty.library-waiting { min-height: 160px; padding: 25px 20px; }
.library-waiting > .mdi { margin-bottom: 10px; font-size: 28px; }
.library-waiting h2 { font-size: 18px; }
.library-download-error { margin: 18px 0 0; color: #ff959a; font-size: 13px; line-height: 1.7; }
.library-intro { margin: 14px 0 0; color: #949eae; font-size: 13px; line-height: 1.7; }
.library-downloads { margin-top: 26px; }
.library-toolbar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
.library-filters { display: flex; flex-wrap: wrap; gap: 8px; }
.search-scope { color: #cbb65c; font-size: 12px; line-height: 1.7; }
.library-search { display: flex; align-items: center; gap: 8px; width: 285px; max-width: 100%; min-height: 42px; padding: 0 12px; box-sizing: border-box; border: 1px solid #30353d; border-radius: 8px; background: #0b0d10; color: #8793a5; }
.library-search:focus-within { border-color: #b49b31; }
.library-search > .mdi { font-size: 18px; }
.library-search input { flex: 1; min-width: 0; width: 100%; padding: 11px 0; border: 0; background: transparent; color: #edf0f4; font: inherit; font-size: 12px; outline: none; }
.library-search input::placeholder { color: #8793a5; opacity: 1; }
.library-search input::-webkit-search-cancel-button { display: none; }
.library-search button { display: grid; place-items: center; width: 26px; height: 28px; padding: 0; border: 0; background: transparent; color: #a4afbf; cursor: pointer; font-size: 17px; }
.library-search button:hover { color: #f1d365; }
.library-search button:focus-visible { outline: 2px solid #ffd000; outline-offset: 1px; }
.search-result { margin: -5px 0 15px; color: #949eae; font-size: 12px; }
.utility-library .library-guide { margin-top: 34px; padding-top: 28px; border-top: 1px solid #292e35; }
.library-filters button { display: inline-flex; align-items: center; gap: 9px; min-height: 42px; padding: 9px 15px; border: 1px solid #30353d; border-radius: 8px; background: #0b0d10; color: #a4afbf; font: inherit; font-size: 13px; cursor: pointer; }
.library-filters button:hover { border-color: #8c7927; color: #f1d365; }
.library-filters button[aria-pressed="true"] { border-color: #b49b31; background: #201c0d; color: #f1d365; }
.library-filters button:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
.filter-count { display: inline-grid; place-items: center; min-width: 19px; height: 19px; padding: 0 3px; box-sizing: border-box; border-radius: 5px; background: #ffffff0b; font-size: 11px; }
.category-empty { padding: 40px 20px; border: 1px solid #2b3038; border-radius: 12px; color: #949eae; text-align: center; font-size: 14px; }
.resource-meta { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.download-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.resource-card { display: flex; flex-direction: column; min-width: 0; padding: 18px; border: 1px solid #343b45; border-radius: 13px; background: #0b0d10; }
.resource-type { display: flex; align-items: center; gap: 8px; color: #cbb65c; font-size: 11px; }
.resource-type .mdi { font-size: 18px; }
.resource-card h2 { margin: 12px 0 8px; color: #edf0f4; font-size: 16px; line-height: 1.5; overflow-wrap: anywhere; }
.resource-card p { margin: 0 0 12px; color: #a4afbf; font-size: 12px; line-height: 1.7; }
.resource-description { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.resource-card a { margin-top: auto; display: flex; justify-content: center; align-items: center; gap: 8px; min-height: 36px; padding: 8px 10px; border: 1px solid #71601e; border-radius: 7px; background: #211d0d; color: #f1d365; text-decoration: none; font-size: 12px; font-weight: 600; }
.resource-card a:hover { border-color: #d3b72d; background: #30290d; }
.resource-card a:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
.library-pagination { display: flex; justify-content: center; align-items: center; gap: 6px; margin: 24px 0 0; }
.library-pagination button, .page-ellipsis { display: inline-grid; place-items: center; width: 34px; height: 34px; padding: 0; color: #a4afbf; font: inherit; font-size: 12px; }
.library-pagination button { border: 1px solid #30353d; border-radius: 6px; background: #0b0d10; cursor: pointer; }
.library-pagination button[aria-current="page"] { border-color: #b49b31; background: #201c0d; color: #f1d365; }
.library-pagination button:hover:not(:disabled) { border-color: #b49b31; color: #f1d365; }
.library-pagination button:disabled { opacity: .35; cursor: default; }
.library-pagination button:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
@media (max-width: 900px) { .download-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { .library-search { width: 100%; } .utility-library .library-guide { margin-top: 28px; padding-top: 24px; } .download-grid { grid-template-columns: minmax(0, 1fr); gap: 13px; } .resource-card { padding: 18px; } .library-pagination { gap: 3px; } .library-pagination button, .page-ellipsis { width: 28px; height: 34px; } }
@media (max-width: 600px) { .utility-library { padding-top: 32px; } .library-empty { min-height: 280px; } }
</style>
