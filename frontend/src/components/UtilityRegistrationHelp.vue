<template>
  <aside class="registration-help" :aria-label="$t('계좌 등록 안내')">
    <ol class="registration-flow">
      <li>{{ $t('전용 링크 가입') }}</li><li>{{ $t('계좌 등록 확인') }}</li><li>{{ $t('자료실 이용') }}</li>
    </ol>
    <p>{{ $t('전용 링크로 가입한 뒤, {channel}으로 인피녹스 계좌번호를 보내 등록을 요청해 주세요.', { channel: $t($locale === 'en' ? '텔레그램' : '카카오톡') }) }}</p>
    <a :href="contactUrl" target="_blank" rel="noopener noreferrer"><span class="mdi mdi-message-text-outline" aria-hidden="true"></span>{{ $t('계좌 등록 요청하기') }}<span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
  </aside>
</template>

<script>
import { businessContacts, serviceUrl } from '../data/serviceLinks'
export default {
  name: 'UtilityRegistrationHelp',
  computed: { contactUrl() { return this.$locale === 'en' ? businessContacts.telegram : serviceUrl('development') } },
}
</script>

<style scoped>
.registration-help { margin-top: 18px; padding: 13px 14px; border: 1px solid #30353d; border-radius: 8px; background: #0d1013; }
.registration-flow { display: flex; flex-wrap: wrap; align-items: center; gap: 5px 8px; margin: 0 0 9px; padding: 0; list-style: none; }
.registration-flow li { display: inline-flex; align-items: center; gap: 8px; color: #d7cb8d; font-size: 11px; line-height: 1.7; white-space: nowrap; }
.registration-flow li + li::before { content: '→'; color: #788391; }
.registration-help p { margin: 0; color: #a6b0bf; font-size: 12px; line-height: 1.8; word-break: keep-all; overflow-wrap: anywhere; }
.registration-help a { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; color: #e3ca65; font-size: 12px; line-height: 1.6; text-decoration: none; }
.registration-help a:hover { color: #ffe17a; text-decoration: underline; }
.registration-help a:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
</style>
