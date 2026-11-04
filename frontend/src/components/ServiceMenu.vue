<template>
  <section class="service-menu" :aria-label="$t('MOCONIX 서비스')">
    <nav class="service-list" :aria-label="$t('서비스 바로가기')">
      <component
        :is="elementFor(item)"
        v-for="item in services"
        :key="item.key"
        v-bind="attributesFor(item)"
        class="service-row"
        @pointerenter="prepareAction(item)"
        @focus="prepareAction(item)"
        @click="activate(item)"
      >
        <span v-if="item.logo" class="service-logo-frame" aria-hidden="true"><img class="service-logo" :class="{ 'service-logo--mt5': item.key === 'free' }" :src="item.logo" :srcset="item.logoSrcset" alt="" /></span>
        <span v-else class="service-symbol mdi" :class="item.icon" aria-hidden="true"></span>
        <span class="service-copy"><span class="service-title">{{ $t(item.title) }}</span><span class="service-description">{{ $t(item.description) }}</span></span>
        <span class="service-arrow mdi" :class="item.external ? 'mdi-arrow-top-right' : 'mdi-arrow-right'" aria-hidden="true"></span>
      </component>
    </nav>

    <component :is="dialogComponent" v-if="dialogComponent" v-model="notice" />
  </section>
</template>

<script>
import { markRaw } from 'vue'
import { utilityRequest } from '../lib/utilityAccess'
import { businessContacts, serviceUrl } from '../data/serviceLinks'
import { kakaotalk as kakaotalkLogo, kmong as kmongLogo, infinox as infinoxLogo, utility as utilityLogo, telegram as telegramLogo } from '../assets/brand/responsive'
let dialogLoad
function loadDialog() {
  if (!dialogLoad) {
    dialogLoad = import(/* webpackChunkName: "service-dialog" */ './ServiceActionDialog.vue')
      .catch(error => { dialogLoad = null; throw error })
  }
  return dialogLoad
}

export default {
  name: 'ServiceMenu',
  data() {
    return {
      notice: '',
      dialogComponent: null,
      noticeRequest: 0,
      checkingLibrary: false,
      baseServices: [
        { key: 'development', title: '개발 의뢰', description: '카카오톡으로 상담하기', logo: kakaotalkLogo.src, logoSrcset: kakaotalkLogo.srcset, external: true },
        { key: 'reviews', title: '개발 실적·후기', description: '판매 내역과 고객 후기', logo: kmongLogo.src, logoSrcset: kmongLogo.srcset, external: true },
        { key: 'free', title: '무료 EA·인디케이터', description: '가입 확인 고객 전용', logo: utilityLogo.src, logoSrcset: utilityLogo.srcset, external: false },
        { key: 'infinox', title: '인피녹스 가입 안내', description: '가입 방법과 이용 안내', logo: infinoxLogo.src, logoSrcset: infinoxLogo.srcset, external: false },
        { key: 'business', title: '비즈니스 제안', description: '공동 개발 · 콘텐츠 협업 등', icon: 'mdi-handshake-outline', external: false },
      ],
    }
  },
  computed: {
    services() {
      return this.baseServices.map(item => item.key === 'development' && this.$locale === 'en'
        ? { ...item, description: '텔레그램으로 상담하기', logo: telegramLogo.src, logoSrcset: telegramLogo.srcset, href: businessContacts.telegram }
        : item)
    },
  },
  methods: {
    prepareAction(item) {
      if (!this.urlFor(item)) loadDialog().catch(() => {})
    },
    async openNotice(key) {
      const request = ++this.noticeRequest
      try {
        const dialog = await loadDialog()
        if (request !== this.noticeRequest) return
        if (!this.dialogComponent) {
          this.dialogComponent = markRaw(dialog.default)
          // Mount the closed dialog first, preserving its existing opening transition.
          await this.$nextTick()
        }
        if (request !== this.noticeRequest) return
        this.notice = key
      } catch { /* Keep the service list usable and allow a later click to retry. */ }
    },
    urlFor(item) { return item.href || serviceUrl(item.key) },
    elementFor(item) { return this.urlFor(item) ? 'a' : 'button' },
    attributesFor(item) {
      const href = this.urlFor(item)
      return href ? { href, target: '_blank', rel: 'noopener noreferrer' } : { type: 'button', disabled: item.key === 'free' && this.checkingLibrary, 'aria-busy': item.key === 'free' && this.checkingLibrary }
    },
    async activate(item) {
      if (this.urlFor(item)) return
      if (item.key !== 'free') { await this.openNotice(item.key); return }
      if (this.checkingLibrary) return
      this.checkingLibrary = true
      try {
        const session = await utilityRequest('session')
        if (session.authenticated) { await this.$router.push('/utilities'); return }
      } catch { /* Keep the sign-in entry available if the session check cannot complete. */ }
      finally { this.checkingLibrary = false }
      await this.openNotice('free')
    },
  },
}
</script>

<style scoped>
.service-menu { --service-icon-size: 28px; width: 100%; max-width: var(--content-width); min-width: 0; text-align: left; color: #fff; }
.service-list { display: grid; grid-template-columns: minmax(0, 1fr); grid-auto-rows: 1fr; gap: 12px; }
.service-row { display: grid; grid-template-columns: var(--service-icon-size) minmax(0, 1fr) 32px; align-items: center; gap: 20px; width: 100%; min-height: 100px; padding: 19px 24px; border: 1px solid #292c31; border-radius: 16px; background: linear-gradient(125deg, #101113, #090a0b); color: #fff; font: inherit; text-decoration: none; text-align: left; cursor: pointer; transition: background .18s, border-color .18s; }
.service-logo-frame { display: grid; place-items: center; width: var(--service-icon-size); height: var(--service-icon-size); overflow: hidden; border-radius: 4px; }
.service-logo { display: block; width: 100%; height: 100%; object-fit: contain; border-radius: 4px; }
.service-logo--mt5 { transform: scale(1.7); }
.service-symbol { display: grid; place-items: center; width: var(--service-icon-size); height: var(--service-icon-size); color: #a4abb6; font-size: var(--service-icon-size); line-height: 1; }
.service-copy { display: flex; flex-direction: column; min-width: 0; gap: 6px; word-break: keep-all; overflow-wrap: anywhere; }
.service-title { font-size: 20px; font-weight: 600; line-height: 1.45; letter-spacing: -.025em; }
.service-description { color: #969da9; font-size: 14px; line-height: 1.7; }
.service-arrow { display: grid; place-items: center; justify-self: end; width: 32px; height: 32px; border: 1px solid #292c31; border-radius: 50%; background: #15171a; color: #a4abb6; font-size: 20px; line-height: 1; transition: color .18s, border-color .18s, background .18s; }
@media (hover: hover) {
  .service-row:hover { border-color: #a68c25; background: linear-gradient(125deg, #19170d, #10100b); }
  .service-row:hover .service-title, .service-row:hover .service-symbol { color: #ffd000; }
  .service-row:hover .service-arrow { color: #ffd000; border-color: #6c5c22; background: #24200f; }
}
.service-row:focus-visible { outline: 2px solid #ffd000; outline-offset: 4px; }
@media (max-width: 600px) {
  .service-menu { --service-icon-size: 26px; }
  .service-row { grid-template-columns: var(--service-icon-size) minmax(0, 1fr) 28px; gap: 14px; min-height: 94px; padding: 17px 18px; border-radius: 14px; }
  .service-title { font-size: 18px; }
  .service-description { font-size: 13px; }
  .service-arrow { width: 28px; height: 28px; font-size: 18px; }
}
@media (prefers-reduced-motion: reduce) { .service-row, .service-arrow { transition: none; } }
</style>
