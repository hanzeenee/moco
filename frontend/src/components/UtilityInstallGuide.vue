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
          <div><h3>{{ $t(step.title) }}</h3>
            <p v-if="step.toolbar" class="toolbar-instruction">{{ toolbarInstruction[0] }}<img class="toolbar-inline-image" :src="$locale === 'en' ? algoTradingEn : systemTradingKo" :alt="$t('시스템트레이딩')" />{{ toolbarInstruction[1] }}</p>
            <p v-else>{{ $t(step.body) }}</p><code v-if="step.path">{{ step.path }}</code>
            <div v-if="step.paths" class="install-paths"><div v-for="path in step.paths" :key="path.value"><span>{{ $t(path.label) }}</span><code>{{ path.value }}</code></div></div>
            <aside v-if="activeType === 'indicator' && index === 0 && authBridge" class="auth-bridge-download" :aria-label="$t('MOCONIX 인증 도우미')">
              <h4><span class="mdi mdi-shield-check-outline" aria-hidden="true"></span>{{ $t(authBridge.title) }}</h4>
              <p>{{ $t(authBridge.description) }}</p>
              <div><code>{{ authBridge.filename }}</code><a :href="authBridge.download_url" download><span class="mdi mdi-download" aria-hidden="true"></span>{{ $t('EX5 다운로드') }}</a></div>
            </aside>
      <aside v-if="step.license" class="license-settings" aria-labelledby="license-settings-title">
        <h3 id="license-settings-title"><span class="mdi mdi-link-variant" aria-hidden="true"></span>{{ $t(activeType === 'indicator' ? '인증 도우미 WebRequest 설정' : '온라인 인증이 필요한 EA') }}</h3>
        <p>{{ $t(activeType === 'indicator' ? '인증 도우미를 적용하기 전에 도구 → 옵션 → 시스템트레이딩에서 WebRequest를 허용하고 아래 주소를 추가해 주세요.' : '차트에 적용하기 전에 도구 → 옵션 → 시스템트레이딩에서 WebRequest를 허용하고 아래 주소를 추가해 주세요.') }}</p>
        <div class="license-url"><code>{{ licenseUrl }}</code><button type="button" @click="copyLicenseUrl">{{ $t(copyState === 'copied' ? '복사 완료' : '주소 복사') }}</button></div>
        <p class="copy-feedback" role="status">{{ copyState === 'copied' ? $t('주소가 복사되었습니다.') : copyState === 'failed' ? $t('복사하지 못했습니다. 위 주소를 직접 복사해 주세요.') : '' }}</p>
        <p class="license-note">{{ $t(activeType === 'indicator' ? '등록된 계좌로 로그인해 주세요. 인증이 완료되기 전에는 지표가 표시되지 않습니다.' : '등록된 계좌로 로그인한 상태에서 적용해 주세요. 인증에 실패하면 EA가 시작되지 않습니다.') }}</p>
      </aside>
          </div>
        </li>
      </ol>

      <details class="guide-help">
        <summary>{{ $t('파일이 보이지 않거나 실행되지 않나요?') }}<span class="mdi mdi-chevron-down" aria-hidden="true"></span></summary>
        <ul>
          <li>{{ $t('파일 종류에 맞는 폴더에 저장했는지 확인하고, 탐색기를 새로고침하거나 MT5를 다시 실행해 주세요.') }}</li>
          <li v-if="activeType === 'ea'">{{ $t('EA는 개별 설정과 MT5 상단의 시스템트레이딩이 모두 허용되어야 거래할 수 있습니다.') }}</li>
          <li v-if="activeType === 'ea'">{{ $t('온라인 인증 EA는 인터넷 연결과 WebRequest 설정이 필요하며, 전략 테스터에서는 사용할 수 없습니다.') }}</li>
          <li v-if="activeType === 'indicator'">{{ $t('인증 대기가 계속되면 AuthBridge가 별도 차트에서 실행 중인지 확인해 주세요. 인증 오류가 표시되면 WebRequest 주소와 계좌 등록을 확인한 뒤 지표를 다시 적용해 주세요.') }}</li>
          <li v-if="activeType === 'indicator'">{{ $t('온라인 인증 지표는 전략 테스터에서 사용할 수 없습니다.') }}</li>
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
  props: { authBridge: { type: Object, default: null } },
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
    toolbarInstruction() { return this.$t('EA 설정에서 시스템트레이딩을 허용하고, MT5 상단의 {button} 버튼도 활성화해 주세요.').split('{button}') },
    steps() {
      const save = { title: 'EX5 파일 저장', body: 'MT5의 파일 → 데이터 폴더 열기에서 아래 폴더에 다운로드한 EX5 파일을 넣어주세요.', path: this.activeType === 'ea' ? 'MQL5 → Experts' : 'MQL5 → Indicators' }
      return this.activeType === 'ea' ? [
        save,
        { title: '탐색기에서 EA 확인', body: 'MT5 탐색기의 시스템트레이딩에서 마우스 오른쪽 버튼 → 새로고침을 선택해 주세요.' },
        { title: '온라인 인증 설정 확인', body: '온라인 인증을 사용하는 EA만 아래 설정을 추가해 주세요.', license: true },
        { title: '차트에 적용', body: '원하는 종목의 차트를 열고 EA를 끌어다 놓으세요. 해당 EA에 안내된 시간봉과 입력값을 확인해 주세요.' },
        { title: '시스템트레이딩 허용', toolbar: true },
      ] : [
        { title: '두 파일을 각 폴더에 저장', body: '파일 → 데이터 폴더 열기에서 지표와 인증 도우미 EX5 파일을 각각 아래 폴더에 넣어주세요.', paths: [{ label: '인디케이터', value: 'MQL5 → Indicators' }, { label: '인증 도우미', value: 'MQL5 → Experts' }] },
        { title: '온라인 인증 연결 설정', body: '인증 도우미가 계좌 등록 여부를 확인할 수 있도록 아래 주소를 허용해 주세요.', license: true },
        { title: '인증 도우미 적용', body: '다른 EA가 없는 별도 차트에 MOCONIX_AuthBridge를 적용하고 해당 차트를 열어두세요. 지표를 먼저 적용했더라도 도우미가 실행되면 자동으로 인증됩니다. 도우미는 주문 없이 계좌 인증만 처리합니다.' },
        { title: '탐색기에서 지표 확인', body: 'MT5 탐색기의 인디케이터에서 마우스 오른쪽 버튼 → 새로고침을 선택해 주세요.' },
        { title: '지표를 원하는 차트에 적용', body: '사용할 인디케이터를 원하는 차트에 끌어다 놓고 입력값을 확인해 주세요. 처음 적용할 때 등록된 계좌인지 확인합니다.' },
        { title: '인증 완료 후 표시 확인', body: '인증이 완료되면 지표가 표시됩니다. 계좌가 등록되지 않았거나 인증에 실패하면 신호를 표시하지 않습니다.' },
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
.install-paths { display: grid; gap: 11px; margin-top: 13px; }
.install-paths > div { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }
.install-paths span { min-width: 90px; color: #b0bbc9; font-size: 12px; }
.install-paths code { margin-top: 0; }
.auth-bridge-download { margin-top: 16px; padding: 18px; border: 1px solid #625522; border-radius: 9px; background: #15140f; }
.auth-bridge-download h4 { display: flex; align-items: center; gap: 8px; margin: 0 0 8px; color: #e8d885; font-size: 14px; font-weight: 600; }
.auth-bridge-download h4 .mdi { font-size: 19px; }
.auth-bridge-download > div { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-top: 14px; }
.auth-bridge-download code { min-width: 0; max-width: 100%; margin-top: 0; box-sizing: border-box; overflow-wrap: anywhere; }
.auth-bridge-download a { display: inline-flex; align-items: center; justify-content: center; gap: 7px; min-height: 40px; padding: 8px 12px; border: 1px solid #71601e; border-radius: 6px; color: #f1d365; font-size: 12px; font-weight: 600; text-decoration: none; }
.auth-bridge-download a:hover { border-color: #d3b72d; background: #30290d; }
.auth-bridge-download a:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
.toolbar-inline-image { display: inline-block; width: auto; height: 28px; max-width: 100%; margin: 0 4px; vertical-align: middle; object-fit: contain; }
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
  .auth-bridge-download { padding: 15px 13px; }
  .auth-bridge-download h4 { gap: 6px; font-size: 13px; }
  .license-settings { margin-top: 13px; padding: 15px 13px; }
  .license-url { padding: 10px; gap: 9px; }
  .license-url code { font-size: 12px; }
  .toolbar-inline-image { height: 26px; }
}
</style>
