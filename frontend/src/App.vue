<template>
  <v-app class="app-shell">
    <TopBar @go-home="goHome" />

    <v-main class="app-main">
      <router-view v-slot="{ Component }">
        <component :is="Component" :key="$route.path === '/' ? homeViewKey : $route.fullPath" />
      </router-view>
    </v-main>
  </v-app>
</template>

<script>
import TopBar from './components/TopBar.vue'

export default {
  name: 'App',
  components: { TopBar },
  data() {
    return { homeViewKey: 0 }
  },
  methods: {
    async goHome() {
      this.homeViewKey += 1
      await this.$router.push('/')
      await this.$nextTick()
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
    }
  }
}
</script>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  background: #000000;
}

.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-height: 100dvh;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000000;
}
</style>
