<template>
  <div class="infinox-guide">
    <section class="signup-panel" aria-labelledby="infinox-signup-title">
      <div class="signup-brand"><img src="../assets/brand/infinox-mark.png" alt="" /><span>{{ $t('MOCONIX IB 추천 링크') }}</span></div>
      <h2 id="infinox-signup-title">{{ $t('인피녹스 회원가입') }}</h2>
      <p class="signup-description">{{ $t('아래 전용 링크에서 가입을 진행해 주세요.') }}</p>
      <a class="signup-button" :href="links.signup" target="_blank" rel="noopener noreferrer" :aria-label="$t('INFINOX 가입하기 (새 탭)')"><span>{{ $t('INFINOX 가입하기') }}</span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
      <div class="referral-meta"><span class="ib-id">IB ID {{ links.ibId }}</span><span>{{ $t('전용 링크 이용 시 추천인 코드 별도 입력 불필요') }}</span></div>
    </section>

    <section class="guide-section" aria-labelledby="infinox-process-title">
      <div class="section-heading"><h3 id="infinox-process-title">{{ $t('가입 후 이용 안내') }}</h3><span>{{ $t('CS팀 전달 안내 기준') }}</span></div>
      <div class="process-grid">
        <div class="process-card"><span class="process-label">{{ $t('가입 승인') }}</span><strong>{{ $t('평일 10:00부터') }}</strong><p>{{ $t('서류 심사 후 순차적으로 승인됩니다.') }}</p></div>
        <div class="process-card"><span class="process-label">{{ $t('거래계좌 개설') }}</span><strong>{{ $t('승인 후 즉시 개설') }}</strong><p>{{ $t('회원가입 승인이 완료된 뒤 개설할 수 있습니다.') }}</p></div>
        <div class="process-card"><span class="process-label">{{ $t('원화 입금 반영') }}</span><strong>{{ $t('약 3~20분') }}</strong><p>{{ $t('입금 채널에 따라 반영 시간이 다를 수 있습니다.') }}</p></div>
        <div class="process-card"><span class="process-label">{{ $t('은행·암호화폐 출금') }}</span><strong>{{ $t('승인 후 약 30분~5시간') }}</strong><p>{{ $t('평일 10:00~24:00 처리 · 대기열에 따라 추가 시간이 소요될 수 있습니다.') }}</p></div>
      </div>
      <p class="timing-note">{{ $t('처리 시간은 예상 안내이며 심사·이용 채널·대기 상황에 따라 달라질 수 있습니다. 최신 이용 조건은 인피녹스 공식 가이드에서 확인해 주세요.') }}</p>
    </section>

    <section class="guide-section" aria-labelledby="infinox-resources-title">
      <h3 id="infinox-resources-title">{{ $t('공식 가이드 바로가기') }}</h3>
      <nav class="guide-links" :aria-label="$t('인피녹스 공식 이용 가이드')">
        <a :href="links.overview" target="_blank" rel="noopener noreferrer"><span>{{ $t('종합 이용 가이드') }}</span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
        <a :href="links.payments" target="_blank" rel="noopener noreferrer"><span>{{ $t('원화 입출금 가이드') }}</span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
        <a :href="links.support" target="_blank" rel="noopener noreferrer"><span>{{ $t('고객센터 이용 방법') }}</span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
      </nav>
    </section>

    <section class="guide-section" aria-labelledby="infinox-support-title">
      <div class="section-heading support-heading"><h3 id="infinox-support-title">{{ $t('고객센터 문의 전 확인') }}</h3><span>{{ $t('평일 10:00~23:59') }}</span></div>
      <p class="support-description">{{ $t('문의 유형에 맞는 정보를 준비하면 상담이 더 수월합니다.') }}</p>
      <div class="support-topics">
        <details><summary>{{ $t('가입 승인·출금 확인') }}</summary><div class="topic-body">{{ $t('인피녹스에 가입한 이메일 주소를 준비해 주세요.') }}</div></details>
        <details><summary>{{ $t('입금 확인 요청') }}</summary><div class="topic-body">{{ $t('가입 이메일 주소를 알려주세요. 필요 시 이체 확인증을 함께 준비해 주세요.') }}<p>{{ $t('이체 확인증에는 보낸 분·받는 분의 성함과 계좌번호, 이체 날짜, 금액이 확인되어야 합니다.') }}</p></div></details>
        <details><summary>{{ $t('메타트레이더·거래 관련 문의') }}</summary><div class="topic-body"><ul><li>{{ $t('거래계좌 번호와 종목명') }}</li><li>{{ $t('문제된 거래의 주문번호(Ticket)') }}</li><li>{{ $t('문제 상황 설명과 가능한 경우 스크린샷 또는 녹화 영상') }}</li></ul></div></details>
      </div>
      <p class="support-note">{{ $locale === 'en' ? $t('고객센터 자료 전달 안내') + ' ' : '이메일·계좌 정보·이체 확인증은 ' }}<a :href="links.support" target="_blank" rel="noopener noreferrer">{{ $t('인피녹스 공식 상담 채널') }}</a>{{ $t('에 전달해 주세요.') }}</p>
    </section>
  </div>
</template>

<script>
import { infinoxGuide } from '../data/infinoxGuide'

export default {
  name: 'InfinoxGuide',
  computed: { links() { return infinoxGuide } },
}
</script>

<style scoped>
.infinox-guide { color: #c0c5ce; font-size: 14px; line-height: 1.65; }
.signup-panel { padding: 22px; border: 1px solid #66551d; border-radius: 12px; background: linear-gradient(135deg, #211e10, #111210 70%); }
.signup-brand { display: flex; align-items: center; gap: 9px; color: #dac77e; font-size: 12px; letter-spacing: .02em; }
.signup-brand img { width: 26px; height: 26px; object-fit: contain; }
.signup-panel h2 { margin: 12px 0 4px; color: #f7f8fa; font-size: 23px; line-height: 1.4; letter-spacing: -.025em; }
.infinox-guide .signup-description { margin: 0; color: #aeb4bf; font-size: 14px; }
.signup-button { display: flex; align-items: center; justify-content: center; gap: 14px; min-height: 56px; margin-top: 20px; padding: 12px 18px; border: 1px solid #ffd000; border-radius: 8px; background: #ffd000; color: #151515; font-size: 18px; font-weight: 700; text-decoration: none; transition: background .16s, box-shadow .16s; }
.signup-button .mdi { font-size: 23px; }
.signup-button:hover { background: #ffdf46; box-shadow: 0 0 18px #ffd00025; }
.referral-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 12px; margin-top: 12px; color: #aab0bb; font-size: 12px; }
.ib-id { padding: 2px 7px; border: 1px solid #51482a; border-radius: 4px; color: #d1c7a1; white-space: nowrap; font-variant-numeric: tabular-nums; }
.guide-section { margin-top: 24px; }
.infinox-guide h3 { margin: 0 0 10px; color: #edf0f4; font-size: 15px; font-weight: 600; line-height: 1.5; }
.section-heading { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 4px 12px; margin-bottom: 10px; }
.section-heading h3 { margin: 0; }
.section-heading > span { color: #858f9e; font-size: 11px; }
.process-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.process-card { padding: 14px 16px; border: 1px solid #2e3239; border-radius: 8px; background: #16181c; }
.process-label { display: block; color: #929caa; font-size: 12px; }
.process-card strong { display: block; margin-top: 4px; color: #e6eaf0; font-size: 17px; font-weight: 600; }
.infinox-guide .process-card p { margin: 5px 0 0; color: #9ca5b3; font-size: 12px; line-height: 1.65; }
.infinox-guide .timing-note { margin: 10px 0 0; color: #838d9b; font-size: 11px; line-height: 1.7; }
.guide-links { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.guide-links a { display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 48px; padding: 11px 12px; border: 1px solid #343943; border-radius: 7px; color: #cbd2dd; font-size: 12px; text-decoration: none; }
.guide-links .mdi { color: #929caa; font-size: 17px; flex: 0 0 auto; }
.guide-links a:hover { border-color: #86712c; background: #1b1b14; }
.infinox-guide .support-description { margin: 0 0 10px; color: #929caa; font-size: 12px; }
.support-topics { border: 1px solid #2e3239; border-radius: 8px; overflow: hidden; }
.support-topics details + details { border-top: 1px solid #2e3239; }
.support-topics summary { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 14px; color: #cbd2dd; font-size: 13px; list-style: none; cursor: pointer; }
.support-topics summary::-webkit-details-marker { display: none; }
.support-topics summary::after { content: '+'; color: #9da6b3; font-size: 18px; line-height: 1; }
.support-topics details[open] summary::after { content: '-'; }
.support-topics details[open] summary { color: #e9d47d; }
.topic-body { padding: 0 14px 14px; color: #a0a9b6; font-size: 12px; line-height: 1.8; }
.infinox-guide .topic-body p { margin: 7px 0 0; }
.topic-body ul { margin: 0; padding-left: 17px; }
.infinox-guide .support-note { margin: 11px 0 0; color: #838d9b; font-size: 11px; }
.support-note a { color: #b9c4d4; text-underline-offset: 3px; }
a:focus-visible, summary:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
@media (max-width: 600px) {
  .signup-panel { padding: 17px 16px; }
  .signup-panel h2 { font-size: 21px; }
  .signup-button { min-height: 54px; margin-top: 16px; font-size: 17px; }
  .guide-links { grid-template-columns: minmax(0, 1fr); }
  .guide-links a { min-height: 44px; font-size: 13px; }
  .process-card { padding: 12px; }
  .process-card strong { font-size: 15px; }
}
@media (max-width: 400px) {
  .process-grid { grid-template-columns: minmax(0, 1fr); }
  .signup-button { gap: 8px; padding-inline: 9px; font-size: 15px; }
  .signup-button .mdi { font-size: 19px; }
}
@media (prefers-reduced-motion: reduce) { .signup-button { transition: none; } }
</style>
