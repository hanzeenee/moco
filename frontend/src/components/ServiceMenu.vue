<template>
  <section class="service-menu" aria-label="MOCONIX 서비스">
    <component
      :is="elementFor(services[0])"
      v-bind="attributesFor(services[0])"
      class="service-feature"
      @click="activate(services[0])"
    >
      <span class="feature-top"><span class="mdi mdi-arrow-top-right" aria-hidden="true"></span></span>
      <h2>개발 의뢰</h2>
      <p>매매 아이디어를 구체적인 프로그램으로</p>
      <span class="feature-action">카카오톡으로 상담하기 <span class="mdi mdi-arrow-right" aria-hidden="true"></span></span>
    </component>

    <nav class="service-list" aria-label="서비스 바로가기">
      <component
        :is="elementFor(item)"
        v-for="item in services.slice(1)"
        :key="item.key"
        v-bind="attributesFor(item)"
        class="service-row"
        @click="activate(item)"
      >
        <span class="service-symbol mdi" :class="item.icon" aria-hidden="true"></span>
        <span class="service-copy"><span class="service-title">{{ item.title }}</span><span class="service-description">{{ item.description }}</span></span>
        <span class="service-arrow mdi" :class="item.external ? 'mdi-arrow-top-right' : 'mdi-arrow-right'" aria-hidden="true"></span>
      </component>
    </nav>

    <ServiceActionDialog v-model="notice" />
  </section>
</template>

<script>
import ServiceActionDialog from './ServiceActionDialog.vue'
import { serviceUrl } from '../data/serviceLinks'

export default {
  name: 'ServiceMenu',
  components: { ServiceActionDialog },
  data() {
    return {
      notice: '',
      services: [
        { key: 'development', external: true },
        { key: 'reviews', title: '개발 실적·후기', description: '크몽 판매 내역과 고객 후기', icon: 'mdi-check-decagram-outline', external: true },
        { key: 'free', title: '무료 유틸리티 지표', description: '가입 확인 고객 전용', icon: 'mdi-chart-line', external: false },
        { key: 'infinox', title: '인피녹스 가입 안내', description: '가입 방법과 제공 조건 확인', icon: 'mdi-book-open-page-variant-outline', external: false },
        { key: 'business', title: '비즈니스 제안', description: '공동 개발 · 콘텐츠 협업', icon: 'mdi-handshake-outline', external: false },
      ],
    }
  },
  methods: {
    elementFor(item) { return serviceUrl(item.key) ? 'a' : 'button' },
    attributesFor(item) {
      const href = serviceUrl(item.key)
      return href ? { href, target: '_blank', rel: 'noopener noreferrer' } : { type: 'button' }
    },
    activate(item) { if (!serviceUrl(item.key)) this.notice = item.key },
  },
}
</script>

<style scoped>
.service-menu { width: 100%; max-width: 500px; min-width: 0; text-align: left; color: #fff; }
.service-feature { display: flex; flex-direction: column; align-items: stretch; width: 100%; padding: 24px; border: 1px solid #303030; border-radius: 10px; background: #0b0b0b; color: #fff; font: inherit; text-align: left; text-decoration: none; cursor: pointer; transition: background .16s, border-color .16s; }
.feature-top { display: flex; align-items: center; justify-content: flex-end; gap: 12px; color: #969ba3; font-size: 21px; }
.feature-top > :last-child { font-size: 19px; }
.service-feature h2 { margin: 14px 0 7px; font-size: clamp(23px, 2vw, 28px); font-weight: 700; line-height: 1.4; }
.service-feature p { margin: 0; color: #a9adb3; font-size: 14px; line-height: 1.7; word-break: keep-all; overflow-wrap: anywhere; }
.feature-action { display: flex; align-items: center; gap: 12px; margin-top: 22px; color: #a9adb3; font-size: 14px; line-height: 1.6; }
.feature-action .mdi { font-size: 19px; }
.service-list { margin-top: 16px; }
.service-row { display: grid; grid-template-columns: 22px minmax(0, 1fr) 20px; align-items: center; gap: 17px; width: 100%; min-height: 85px; padding: 18px 4px; border: 0; border-bottom: 1px solid #303030; background: transparent; color: #fff; font: inherit; text-decoration: none; text-align: left; cursor: pointer; transition: background .16s, border-color .16s; }
.service-symbol { color: #969ba3; font-size: 22px; }
.service-copy { display: flex; flex-direction: column; min-width: 0; gap: 5px; word-break: keep-all; overflow-wrap: anywhere; }
.service-title { font-size: 17px; font-weight: 600; line-height: 1.5; }
.service-description { color: #969ba3; font-size: 13px; line-height: 1.6; }
.service-arrow { justify-self: end; color: #969ba3; font-size: 18px; }
@media (hover: hover) {
  .service-feature:hover { border-color: #ffd000; background: #13120c; }
  .service-feature:hover h2, .service-feature:hover .feature-top, .service-feature:hover .feature-action { color: #ffd000; }
  .service-row:hover { border-bottom-color: #ffd000; background: #0b0b0b; }
  .service-row:hover .service-title, .service-row:hover .service-arrow, .service-row:hover .service-symbol { color: #ffd000; }
}
.service-row:focus-visible, .service-feature:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
@media (max-width: 600px) {
  .service-feature { padding: 22px; }
  .service-row { gap: 14px; min-height: 82px; }
  .service-title { font-size: 16px; }
}
@media (prefers-reduced-motion: reduce) { .service-feature, .service-row { transition: none; } }
</style>
