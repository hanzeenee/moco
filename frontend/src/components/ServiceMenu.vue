<template>
  <section class="service-menu" aria-label="MOCONIX 서비스">
    <nav class="service-list" aria-label="서비스 바로가기">
      <component
        :is="elementFor(item)"
        v-for="item in services"
        :key="item.key"
        v-bind="attributesFor(item)"
        class="service-row"
        @click="activate(item)"
      >
        <span v-if="item.logo" class="service-logo-frame" aria-hidden="true"><img class="service-logo" :class="{ 'service-logo--mt5': item.key === 'free' }" :src="item.logo" alt="" /></span>
        <span v-else class="service-symbol mdi" :class="item.icon" aria-hidden="true"></span>
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
import kakaotalkLogo from '../assets/brand/kakaotalk-mark.png'
import kmongLogo from '../assets/brand/kmong-mark.png'
import infinoxLogo from '../assets/brand/infinox-mark.png'
import utilityLogo from '../assets/brand/utility-indicator.png'

export default {
  name: 'ServiceMenu',
  components: { ServiceActionDialog },
  data() {
    return {
      notice: '',
      services: [
        { key: 'development', title: '개발 의뢰', description: '카카오톡으로 상담하기', logo: kakaotalkLogo, external: true },
        { key: 'reviews', title: '개발 실적·후기', description: '판매 내역과 고객 후기', logo: kmongLogo, external: true },
        { key: 'free', title: '무료 유틸리티 지표', description: '가입 확인 고객 전용', logo: utilityLogo, external: false },
        { key: 'infinox', title: '인피녹스 가입 안내', description: '가입 방법과 제공 조건 확인', logo: infinoxLogo, external: false },
        { key: 'business', title: '비즈니스 제안', description: '공동 개발 · 콘텐츠 협업 등', icon: 'mdi-handshake-outline', external: false },
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
.service-menu { --service-icon-size: 28px; width: 100%; max-width: 560px; min-width: 0; text-align: left; color: #fff; }
.service-list { display: grid; grid-template-columns: minmax(0, 1fr); grid-auto-rows: 1fr; gap: 12px; }
.service-row { display: grid; grid-template-columns: var(--service-icon-size) minmax(0, 1fr) 24px; align-items: center; gap: 20px; width: 100%; min-height: 100px; padding: 18px 24px; border: 1px solid #303030; border-radius: 12px; background: #0b0b0b; color: #fff; font: inherit; text-decoration: none; text-align: left; cursor: pointer; transition: background .16s, border-color .16s; }
.service-logo-frame { display: grid; place-items: center; width: var(--service-icon-size); height: var(--service-icon-size); overflow: hidden; border-radius: 3px; }
.service-logo { display: block; width: 100%; height: 100%; object-fit: contain; border-radius: 3px; }
.service-logo--mt5 { transform: scale(1.7); }
.service-symbol { display: grid; place-items: center; width: var(--service-icon-size); height: var(--service-icon-size); color: #969ba3; font-size: var(--service-icon-size); line-height: 1; }
.service-copy { display: flex; flex-direction: column; min-width: 0; gap: 6px; word-break: keep-all; overflow-wrap: anywhere; }
.service-title { font-size: 20px; font-weight: 600; line-height: 1.5; }
.service-description { color: #969ba3; font-size: 15px; line-height: 1.6; }
.service-arrow { justify-self: end; color: #969ba3; font-size: 22px; }
@media (hover: hover) {
  .service-row:hover { border-color: #ffd000; background: #13120c; }
  .service-row:hover .service-title, .service-row:hover .service-arrow, .service-row:hover .service-symbol { color: #ffd000; }
}
.service-row:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
@media (max-width: 600px) {
  .service-menu { --service-icon-size: 26px; }
  .service-row { gap: 16px; min-height: 94px; padding: 16px 20px; }
  .service-description { font-size: 14px; }
  .service-arrow { font-size: 20px; }
  .service-title { font-size: 18px; }
}
@media (prefers-reduced-motion: reduce) { .service-row { transition: none; } }
</style>
