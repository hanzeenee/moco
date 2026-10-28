<template>
  <v-dialog :model-value="Boolean(modelValue)" max-width="460" theme="dark" aria-labelledby="service-dialog-title" @update:model-value="!$event && close()">
    <v-card class="service-dialog">
      <v-card-title id="service-dialog-title" class="service-dialog-title">{{ content.title }}</v-card-title>
      <v-card-text class="service-dialog-text">
        <p v-for="paragraph in content.paragraphs" :key="paragraph">{{ paragraph }}</p>
        <div v-if="modelValue === 'business'" class="business-contacts">
          <a class="contact-link" :href="contacts.email"><span class="mdi mdi-email-outline" aria-hidden="true"></span><span><strong>이메일</strong><span>moconix95@gmail.com</span></span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
          <a class="contact-link" :href="contacts.telegram" target="_blank" rel="noopener noreferrer"><span class="mdi mdi-send-outline" aria-hidden="true"></span><span><strong>텔레그램</strong><span>@moconix</span></span><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></a>
        </div>
      </v-card-text>
      <v-card-actions class="service-dialog-actions">
        <v-spacer />
        <v-btn variant="text" @click="close">닫기</v-btn>
        <v-btn v-if="modelValue === 'free'" variant="text" @click="$emit('update:modelValue', 'infinox')">가입 안내 보기</v-btn>
        <v-btn v-if="modelValue === 'free'" class="service-dialog-primary" :href="contactUrl" target="_blank" rel="noopener noreferrer" @click="close">카카오톡으로 문의하기</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { VDialog, VCard, VCardTitle, VCardText, VCardActions, VSpacer, VBtn } from 'vuetify/components'
import { businessContacts, serviceUrl } from '../data/serviceLinks'

const notices = {
  development: {
    title: '개발 의뢰',
    paragraphs: ['MT5 EA, 인디케이터, TradingView 지표 제작을 상담할 수 있어요.', '카카오톡 상담 연결을 준비 중입니다.'],
  },
  reviews: {
    title: '개발 실적·후기',
    paragraphs: ['크몽 판매 내역과 고객 후기를 확인할 수 있는 페이지를 준비 중입니다.'],
  },
  free: {
    title: '무료 유틸리티 지표',
    paragraphs: ['인피녹스 가입이 확인된 고객에게 제공되는 자료입니다.', '카카오톡에서 가입 확인 후 전용 그룹방으로 초대해 드립니다.'],
  },
  business: {
    title: '비즈니스 제안',
    paragraphs: ['공동 개발, 콘텐츠 협업 등 비즈니스 제안을 보내주세요.'],
  },
  infinox: {
    title: '인피녹스 가입 안내',
    paragraphs: ['인피녹스 가입 방법과 상세 안내를 준비 중입니다.', '가입 안내가 준비되면 이곳에서 확인할 수 있어요.'],
  },
}

export default {
  name: 'ServiceActionDialog',
  components: { VDialog, VCard, VCardTitle, VCardText, VCardActions, VSpacer, VBtn },
  props: { modelValue: { type: String, default: '' } },
  emits: ['update:modelValue'],
  computed: {
    content() { return notices[this.modelValue] || { title: '', paragraphs: [] } },
    contacts() { return businessContacts },
    contactUrl() { return serviceUrl('development') },
  },
  methods: { close() { this.$emit('update:modelValue', '') } },
}
</script>

<style scoped>
.service-dialog { background: #111 !important; border: 1px solid #353535; border-radius: 12px !important; padding: 10px; }
.service-dialog-title { color: #fff; font-size: 21px; white-space: normal; padding: 18px 18px 8px; }
.service-dialog-text { color: #bdc1c8; font-size: 15px; line-height: 1.9; padding: 12px 18px !important; word-break: keep-all; overflow-wrap: anywhere; }
.service-dialog-text p + p { margin-top: 12px; }
.service-dialog-actions { flex-wrap: wrap; gap: 4px; padding: 10px; }
.service-dialog-primary { background: #ffd000; color: #000 !important; }
.business-contacts { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }
.contact-link { display: grid; grid-template-columns: 22px minmax(0, 1fr) 16px; gap: 12px; align-items: center; padding: 14px; border: 1px solid #383838; border-radius: 7px; color: #d4d8df; text-decoration: none; }
.contact-link > span:nth-child(2) { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.contact-link strong { font-size: 13px; font-weight: 500; color: #a5a9b0; }
.contact-link > span:nth-child(2) > span { color: #fff; overflow-wrap: anywhere; }
.contact-link:hover { background: #1a1a1a; border-color: #b6981d; }
.contact-link:focus-visible { outline: 2px solid #ffd000; outline-offset: 3px; }
@media (max-width: 480px) {
  .contact-link { grid-template-columns: 20px minmax(0, 1fr) 16px; gap: 8px; padding: 12px; }
  .contact-link > span:nth-child(2) { display: contents; }
  .contact-link strong { grid-column: 2; grid-row: 1; }
  .contact-link > span:nth-child(2) > span { grid-column: 1 / -1; grid-row: 2; font-size: 14px; }
  .contact-link > .mdi:last-child { grid-column: 3; grid-row: 1; }
}
</style>
