<template>
  <v-dialog :model-value="Boolean(modelValue)" :max-width="modelValue === 'infinox' ? 760 : 460" theme="dark" aria-labelledby="service-dialog-title" @update:model-value="!$event && close()">
    <v-card class="service-dialog" :class="{ 'infinox-dialog': modelValue === 'infinox' }">
      <v-card-title id="service-dialog-title" class="service-dialog-title">{{ $t(content.title) }}</v-card-title>
      <v-card-text class="service-dialog-text">
        <InfinoxGuide v-if="modelValue === 'infinox'" />
        <UtilityAccountLogin v-if="modelValue === 'utility-login'" @authenticated="close" />
        <p v-for="paragraph in modelValue === 'infinox' ? [] : content.paragraphs" :key="paragraph">{{ $t(paragraph) }}</p>
        <div v-if="modelValue === 'business'" class="business-contacts">
          <a class="contact-link" :href="contacts.email"><img class="gmail-icon" src="../assets/brand/gmail-mark.png" alt="" aria-hidden="true" /><span><strong>{{ $t('이메일') }}</strong><span>moconix95@gmail.com</span></span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
          <a class="contact-link" :href="contacts.telegram" target="_blank" rel="noopener noreferrer"><img class="telegram-icon" src="../assets/brand/telegram-color-mark.png" alt="" aria-hidden="true" /><span><strong>{{ $t('텔레그램') }}</strong><span>@moconix</span></span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
        </div>
      </v-card-text>
      <v-card-actions class="service-dialog-actions" :class="{ 'free-dialog-actions': modelValue === 'free' }">
        <div v-if="modelValue === 'free'" class="free-action-group">
          <v-btn class="service-dialog-primary" @click="$emit('update:modelValue', 'utility-login')">{{ $t('로그인') }}</v-btn>
          <v-btn variant="text" @click="$emit('update:modelValue', 'infinox')">{{ $t('가입 안내 보기') }}</v-btn>
        </div>
        <v-btn variant="text" @click="close">{{ $t('닫기') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { VDialog, VCard, VCardTitle, VCardText, VCardActions, VBtn } from 'vuetify/components'
import { businessContacts } from '../data/serviceLinks'
import UtilityAccountLogin from './UtilityAccountLogin.vue'
import InfinoxGuide from './InfinoxGuide.vue'

const notices = {
  'utility-login': { title: '인피녹스 계좌번호', paragraphs: [] },
  development: {
    title: '개발 의뢰',
    paragraphs: ['MT5 EA, 인디케이터, TradingView 지표 제작을 상담할 수 있어요.', '카카오톡 상담 연결을 준비 중입니다.'],
  },
  reviews: {
    title: '개발 실적·후기',
    paragraphs: ['판매 내역과 고객 후기를 확인할 수 있는 페이지를 준비 중입니다.'],
  },
  free: {
    title: '무료 EA·인디케이터',
    paragraphs: ['MOCONIX 추천 링크로 가입하고 계좌 등록이 확인된 고객을 위한 전용 자료실입니다.', '등록된 인피녹스 계좌번호로 로그인하면 자료실로 이동합니다.'],
  },
  business: {
    title: '비즈니스 제안',
    paragraphs: ['공동 개발, 콘텐츠 협업 등 비즈니스 제안을 보내주세요.'],
  },
  infinox: {
    title: '인피녹스 가입 안내',
    paragraphs: [],
  },
}

export default {
  name: 'ServiceActionDialog',
  components: { VDialog, VCard, VCardTitle, VCardText, VCardActions, VBtn, InfinoxGuide, UtilityAccountLogin },
  props: { modelValue: { type: String, default: '' } },
  emits: ['update:modelValue'],
  computed: {
    content() { return notices[this.modelValue] || { title: '', paragraphs: [] } },
    contacts() { return businessContacts },
  },
  methods: { close() { this.$emit('update:modelValue', '') } },
}
</script>

<style scoped>
.service-dialog { background: #111 !important; border: 1px solid #353535; border-radius: 12px !important; padding: 10px; }
.service-dialog-title { color: #fff; font-size: 21px; white-space: normal; padding: 18px 18px 8px; }
.service-dialog-text { color: #bdc1c8; font-size: 15px; line-height: 1.9; padding: 12px 18px !important; word-break: keep-all; overflow-wrap: anywhere; }
.service-dialog-text p + p { margin-top: 12px; }
.service-dialog-actions { justify-content: flex-end; flex-wrap: wrap; gap: 4px; padding: 10px; }
.service-dialog-actions > .v-btn, .free-action-group > .v-btn { margin-inline-start: 0 !important; }
.free-dialog-actions { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 12px; }
.free-action-group { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; min-width: 0; }
.free-action-group > .v-btn { min-width: 0; max-width: 100%; }
.free-action-group :deep(.v-btn__content) { white-space: normal; text-align: center; }
.service-dialog-primary { background: #ffd000; color: #000 !important; }
.service-dialog.infinox-dialog { padding: 0; max-height: calc(100dvh - 48px); }
.infinox-dialog .service-dialog-title { flex: 0 0 auto; padding: 23px 26px 12px; font-size: 24px; }
.infinox-dialog .service-dialog-text { min-height: 0; overflow-y: auto; padding: 4px 26px 22px !important; overscroll-behavior: contain; }
.infinox-dialog .service-dialog-actions { flex: 0 0 auto; padding: 10px 20px; border-top: 1px solid #2c3036; background: #111; }
.business-contacts { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }
.contact-link { display: grid; grid-template-columns: 22px minmax(0, 1fr) 16px; gap: 12px; align-items: center; padding: 14px; border: 1px solid #383838; border-radius: 7px; color: #d4d8df; text-decoration: none; }
.contact-link > span:nth-child(2) { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.gmail-icon, .telegram-icon { display: block; width: 20px; height: 20px; object-fit: contain; }
.contact-link strong { font-size: 13px; font-weight: 500; color: #a5a9b0; }
.contact-link > span:nth-child(2) > span { color: #fff; overflow-wrap: anywhere; }
.contact-link:hover { background: #1a1a1a; border-color: #b6981d; }
.contact-link:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
@media (max-width: 480px) {
  .infinox-dialog .service-dialog-title { padding: 18px 16px 12px; font-size: 21px; }
  .infinox-dialog .service-dialog-text { padding: 4px 16px 18px !important; }
  .infinox-dialog .service-dialog-actions { padding: 8px 12px; }
  .contact-link { grid-template-columns: 20px minmax(0, 1fr) 16px; gap: 8px; padding: 12px; }
  .contact-link > span:nth-child(2) { display: contents; }
  .gmail-icon, .telegram-icon { display: block; width: 20px; height: 20px; object-fit: contain; }
.contact-link strong { grid-column: 2; grid-row: 1; }
  .contact-link > span:nth-child(2) > span { grid-column: 1 / -1; grid-row: 2; font-size: 14px; }
  .contact-link > .mdi:last-child { grid-column: 3; grid-row: 1; }
}
</style>
