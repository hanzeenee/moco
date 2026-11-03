import { createApp } from 'vue'
import App from './App.vue'
import { installLanguage } from './i18n'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import store from './store'
import router from './router'

loadFonts()

const app = createApp(App)
  .use(installLanguage)
  .use(store)
  .use(vuetify)
  .use(router)

// Keep the build-time homepage visible until the current route is ready.
router.isReady().then(() => app.mount('#app'))