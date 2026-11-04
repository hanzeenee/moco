// Build-only entry: render the same public homepage without a browser or server.
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { createStore } from 'vuex'
import App from './App.vue'
import { createAppRouter } from './router'
import { installLanguage, setLanguage, t } from './i18n'
import { createAppVuetify } from './plugins/vuetify'

// Match the current browser app's literal shell elements exactly. They are not
// registered Vuetify components in the existing CSR entry, so no extra wrappers
// or layout styles may appear during the initial HTML paint.
const literalShell = tag => ({
  inheritAttrs: false,
  setup(_, { attrs, slots }) { return () => h(tag, attrs, slots.default?.()) },
})

export async function renderHome(locale) {
  setLanguage(locale)
  const router = createAppRouter({ memory: true })
  const app = createSSRApp(App)
    .use(installLanguage)
    .use(createStore({ state: {} }))
    .use(createAppVuetify({ ssr: true }))
    .use(router)
    .component('v-app', literalShell('v-app'))
    .component('v-main', literalShell('v-main'))
  await router.push('/')
  await router.isReady()
  const context = {}
  const html = await renderToString(app, context)
  return {
    html,
    title: t('MOCONIX | MT5 EA·인디케이터 & TradingView 지표 개발'),
    description: t('MT5 EA·인디케이터와 TradingView 지표를 맞춤 개발합니다. 매매 전략과 필요한 기능을 구현하고, 기존 프로그램의 수정 및 개선도 지원합니다.'),
  }
}
