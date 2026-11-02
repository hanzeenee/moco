<template>
  <section class="install-guide" aria-labelledby="install-guide-title">
    <header class="guide-heading">
      <p class="guide-eyebrow">MT5 · EX5</p>
      <h2 id="install-guide-title">{{ $t('설치 및 실행 안내') }}</h2>
      <p>{{ $t('PC용 MT5 기준입니다. 설치할 파일의 종류를 선택해 주세요.') }}</p>
    </header>

    <div class="guide-types" role="group" :aria-label="$t('설치할 프로그램 종류')">
      <button v-for="type in programTypes" :key="type.id" type="button" :class="{ selected: activeType === type.id }" :aria-pressed="activeType === type.id" @click="selectType(type.id)">
        <span :class="['mdi', type.icon]" aria-hidden="true"></span>
        <span><strong>{{ $t(type.name) }}</strong><small>{{ $t(type.description) }}</small></span>
        <span class="mdi mdi-check-circle" aria-hidden="true"></span>
      </button>
    </div>

    <section class="guide-content" :aria-label="$t(activeType === 'ea' ? 'EA 설치 방법' : '인디케이터 설치 방법')">
      <div class="guide-introduction">
        <span class="guide-type-badge">{{ activeType === 'ea' ? 'EA' : $t('인디케이터') }}</span>
        <p>{{ $t(activeType === 'ea' ? '자동으로 거래하는 프로그램입니다. 해당 EA의 설명과 설정을 확인한 뒤 실행해 주세요.' : '차트에 정보나 알림을 표시하는 지표입니다. 아래 순서대로 적용해 주세요.') }}</p>
      </div>

      <ol class="guide-steps" role="list">
        <li v-for="(step, index) in steps" :key="`${activeType}-${index}`">
          <span class="step-number" aria-hidden="true">{{ index + 1 }}</span>
          <div><h3>{{ $t(step.title) }}</h3><p>{{ $t(step.body) }}</p><code v-if="step.path">{{ step.path }}</code>
            <figure v-if="step.toolbar" class="toolbar-example">
              <img :src="$locale === 'en' ? algoTradingEn : systemTradingKo" :alt="$t('한국어 MT5 · 시스템트레이딩 버튼')" />
              <figcaption>{{ $t('한국어 MT5 · 시스템트레이딩 버튼') }}</figcaption>
            </figure>
      <aside v-if="step.license" class="license-settings" aria-labelledby="license-settings-title">
        <h3 id="license-settings-title"><span class="mdi mdi-link-variant" aria-hidden="true"></span>{{ $t('온라인 인증이 필요한 EA') }}</h3>
        <p>{{ $t('차트에 적용하기 전에 도구 → 옵션 → 시스템트레이딩에서 WebRequest를 허용하고 아래 주소를 추가해 주세요.') }}</p>
        <div class="license-url"><code>{{ licenseUrl }}</code><button type="button" @click="copyLicenseUrl">{{ $t(copyState === 'copied' ? '복사 완료' : '주소 복사') }}</button></div>
        <p class="copy-feedback" role="status">{{ copyState === 'copied' ? $t('주소가 복사되었습니다.') : copyState === 'failed' ? $t('복사하지 못했습니다. 위 주소를 직접 복사해 주세요.') : '' }}</p>
        <p class="license-note">{{ $t('등록된 계좌로 로그인한 상태에서 적용해 주세요. 인증에 실패하면 EA가 시작되지 않습니다.') }}</p>
      </aside>
          </div>
        </li>
      </ol>

      <aside v-if="activeType === 'indicator'" class="indicator-note">
        <span class="mdi mdi-information-outline" aria-hidden="true"></span>
        <p>{{ $t('표시·알림용 인디케이터는 시스템트레이딩 버튼을 켤 필요가 없습니다. 추가 설정이 있는 자료는 해당 파일의 안내를 따라주세요.') }}</p>
      </aside>

      <details class="guide-help">
        <summary>{{ $t('파일이 보이지 않거나 실행되지 않나요?') }}<span class="mdi mdi-chevron-down" aria-hidden="true"></span></summary>
        <ul>
          <li>{{ $t('파일 종류에 맞는 폴더에 저장했는지 확인하고, 탐색기를 새로고침하거나 MT5를 다시 실행해 주세요.') }}</li>
          <li v-if="activeType === 'ea'">{{ $t('EA는 개별 설정과 MT5 상단의 시스템트레이딩이 모두 허용되어야 거래할 수 있습니다.') }}</li>
          <li v-if="activeType === 'ea'">{{ $t('온라인 인증 EA는 인터넷 연결과 WebRequest 설정이 필요하며, 전략 테스터에서는 사용할 수 없습니다.') }}</li>
          <li>{{ $t('문제가 계속되면 MT5 하단 로그의 오류 내용과 적용 화면을 함께 문의해 주세요.') }}</li>
        </ul>
      </details>
    </section>
  </section>
</template>

<script>
import systemTradingKo from '../assets/guides/mt5-system-trading-ko.svg'
import algoTradingEn from '../assets/guides/mt5-algo-trading-en.svg'

export default {
  name: 'UtilityInstallGuide',
  data() {
    return {
      activeType: 'ea',
      systemTradingKo,
      algoTradingEn,
      copyState: '',
      licenseUrl: 'https://moconix.com',
      programTypes: [
        { id: 'ea', name: 'EA', description: '자동매매 프로그램', icon: 'mdi-robot' },
        { id: 'indicator', name: '인디케이터', description: '차트 정보 · 알림', icon: 'mdi-chart-line' },
      ],
    }
  },
  computed: {
    steps() {
      const save = { title: 'EX5 파일 저장', body: 'MT5의 파일 → 데이터 폴더 열기에서 아래 폴더에 다운로드한 EX5 파일을 넣어주세요.', path: this.activeType === 'ea' ? 'MQL5 → Experts' : 'MQL5 → Indicators' }
      return this.activeType === 'ea' ? [
        save,
        { title: '탐색기에서 EA 확인', body: 'MT5 탐색기의 시스템트레이딩에서 마우스 오른쪽 버튼 → 새로고침을 선택해 주세요.' },
        { title: '온라인 인증 설정 확인', body: '온라인 인증을 사용하는 EA만 아래 설정을 추가해 주세요.', license: true },
        { title: '차트에 적용', body: '원하는 종목의 차트를 열고 EA를 끌어다 놓으세요. 해당 EA에 안내된 시간봉과 입력값을 확인해 주세요.' },
        { title: '시스템트레이딩 허용', body: 'EA 설정에서 시스템트레이딩을 허용한 뒤, 아래 이미지와 같은 MT5 상단의 시스템트레이딩 버튼을 활성화해 주세요.', toolbar: true },
      ] : [
        save,
        { title: '탐색기에서 지표 확인', body: 'MT5 탐색기의 인디케이터에서 마우스 오른쪽 버튼 → 새로고침을 선택해 주세요.' },
        { title: '차트에 적용', body: '원하는 차트에 인디케이터를 끌어다 놓고, 입력값·색상·알림 등 필요한 설정을 확인한 뒤 적용해 주세요.' },
        { title: '표시 및 알림 확인', body: '차트에 표시되는 정보와 알림이 설정한 대로 동작하는지 확인해 주세요. 사용 가능한 기능은 지표마다 다릅니다.' },
      ]
    },
  },
  methods: {
    selectType(type) { this.activeType = type; this.copyState = '' },
    async copyLicenseUrl() {
      try { await navigator.clipboard.writeText(this.licenseUrl); this.copyState = 'copied' }
      catch { this.copyState = 'failed' }
    },
  },
}
</script>

<style scoped>
.install-guide { margin-top: 38px; }
.guide-heading { margin-bottom: 22px; }
.guide-eyebrow { margin: 0 0 9px !important; color: #b6a65f !important; font-size: 11px !important; letter-spacing: .12em; }
.guide-heading h2 { margin: 0 0 9px; color: #eef0f4; font-size: 24px; font-weight: 650; letter-spacing: -.02em; }
.guide-heading p { margin: 0; color: #99a3b3; font-size: 14px; line-height: 1.7; }
.guide-types { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.guide-types button { display: flex; align-items: center; gap: 14px; min-height: 82px; padding: 16px 20px; border: 1px solid #303640; border-radius: 11px; background: #0b0d10; color: #929dab; text-align: left; font: inherit; cursor: pointer; transition: border-color .15s, background .15s; }
.guide-types button.selected { border-color: #c3a329; background: #17160e; color: #ffd000; }
.guide-types button:hover { border-color: #c3a329; }
.guide-types button > .mdi:first-child { font-size: 27px; flex: 0 0 auto; }
.guide-types strong { display: block; color: #eef0f4; font-size: 17px; font-weight: 650; }
.guide-types small { display: block; margin-top: 4px; color: #99a3b3; font-size: 12px; line-height: 1.5; }
.guide-types .mdi-check-circle { margin-left: auto; font-size: 19px; opacity: 0; }
.guide-types button.selected .mdi-check-circle { opacity: 1; }
button:focus-visible, summary:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
.guide-content { margin-top: 16px; padding: 28px; border: 1px solid #2b3038; border-radius: 14px; background: #0b0d10; }
.guide-introduction { display: flex; align-items: flex-start; gap: 12px; padding-bottom: 24px; border-bottom: 1px solid #252a31; }
.guide-type-badge { flex-shrink: 0; padding: 4px 8px; border: 1px solid #444c59; border-radius: 5px; color: #d2d8e2; font-size: 11px; line-height: 1.7; }
.guide-introduction p { margin: 1px 0 0; color: #b3bcc9; font-size: 14px; line-height: 1.8; }
.guide-steps { display: grid; gap: 26px; margin: 26px 0; padding: 0; list-style: none; }
.guide-steps li { display: grid; grid-template-columns: 28px minmax(0, 1fr); gap: 14px; }
.step-number { display: grid; place-items: center; width: 28px; height: 28px; border: 1px solid #464b51; border-radius: 50%; color: #d9c15d; font-size: 13px; font-weight: 600; }
.guide-steps h3 { margin: 2px 0 7px; color: #e7eaf0; font-size: 15px; font-weight: 600; }
.guide-steps p { margin: 0; color: #a1acbc; font-size: 14px; line-height: 1.8; word-break: keep-all; overflow-wrap: anywhere; }
.guide-steps code { display: inline-block; margin-top: 10px; padding: 8px 13px; border: 1px solid #363e49; border-radius: 6px; background: #070809; color: #e3e8f0; font-size: 13px; }
.toolbar-example { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin: 14px 0 0; padding: 14px 16px; border: 1px solid #343c47; border-radius: 8px; background: #080a0c; }
.toolbar-example img { display: block; width: auto; height: 44px; max-width: 100%; object-fit: contain; }
.toolbar-example figcaption { color: #9da9b8; font-size: 12px; line-height: 1.7; word-break: keep-all; overflow-wrap: anywhere; }
.license-settings { margin-top: 13px; padding: 20px; border: 1px solid #625522; border-radius: 9px; background: #15140f; }
.license-settings h3 { display: flex; align-items: center; gap: 8px; margin: 0 0 9px; color: #e8d885; font-size: 14px; font-weight: 600; }
.license-settings h3 .mdi { font-size: 18px; }
.license-settings p { margin: 0; color: #aab2bf; font-size: 13px; line-height: 1.8; word-break: keep-all; overflow-wrap: anywhere; }
.license-url { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-top: 14px; padding: 10px 12px; border: 1px solid #3c3c30; border-radius: 7px; background: #070809; }
.license-url code { color: #edf0f5; font-size: 14px; overflow-wrap: anywhere; user-select: text; }
.license-url button { flex-shrink: 0; min-height: 36px; padding: 7px 11px; border: 1px solid #6f6020; border-radius: 5px; color: #efd158; font: inherit; font-size: 12px; cursor: pointer; }
.license-url button:hover { background: #26220f; }
.license-settings .copy-feedback { min-height: 20px; margin-top: 5px; color: #d9c878; font-size: 12px; }
.license-settings .license-note { margin-top: 6px; font-size: 12px; }
.indicator-note { display: flex; align-items: flex-start; gap: 10px; padding: 17px 19px; border: 1px solid #34404b; border-radius: 9px; background: #10151a; }
.indicator-note .mdi { color: #a4bacf; font-size: 20px; }
.indicator-note p { margin: 0; color: #aebccc; font-size: 13px; line-height: 1.8; word-break: keep-all; overflow-wrap: anywhere; }
.guide-help { margin-top: 23px; padding-top: 18px; border-top: 1px solid #292f37; }
.guide-help summary { display: flex; justify-content: space-between; align-items: center; gap: 12px; color: #c3cbd7; font-size: 13px; cursor: pointer; list-style: none; }
.guide-help summary::-webkit-details-marker { display: none; }
.guide-help summary .mdi { flex-shrink: 0; color: #8e9aab; font-size: 19px; transition: transform .15s; }
.guide-help[open] summary .mdi { transform: rotate(180deg); }
.guide-help ul { display: grid; gap: 9px; margin: 17px 0 0; padding-left: 18px; color: #929faf; font-size: 13px; line-height: 1.8; }
@media (max-width: 600px) {
  .install-guide { margin-top: 30px; }
  .guide-heading h2 { font-size: 21px; }
  .guide-heading p { font-size: 13px; }
  .guide-types { gap: 9px; }
  .guide-types button { align-items: flex-start; gap: 8px; min-height: 88px; padding: 14px 11px; }
  .guide-types button > .mdi:first-child { font-size: 22px; }
  .guide-types strong { font-size: 15px; }
  .guide-types small { font-size: 11px; }
  .guide-types .mdi-check-circle { display: none; }
  .guide-content { padding: 21px 17px; }
  .guide-introduction { flex-wrap: wrap; gap: 9px; padding-bottom: 21px; }
  .guide-introduction p { flex-basis: 100%; font-size: 13px; }
  .guide-steps { gap: 23px; }
  .guide-steps li { grid-template-columns: 25px minmax(0, 1fr); gap: 11px; }
  .step-number { width: 25px; height: 25px; font-size: 12px; }
  .guide-steps h3 { font-size: 14px; }
  .guide-steps p { font-size: 13px; }
  .guide-steps code { padding: 7px 9px; font-size: 12px; }
  .license-settings { margin-top: 13px; padding: 15px 13px; }
  .license-url { padding: 10px; gap: 9px; }
  .license-url code { font-size: 12px; }
  .indicator-note { padding: 14px 12px; }
  .toolbar-example { gap: 10px; padding: 12px; }
  .toolbar-example img { height: 40px; }
}
</style>
