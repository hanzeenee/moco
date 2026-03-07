<template>
  <v-app>
    <TopBar />

    <v-main class="app-main">
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import TopBar from './components/TopBar.vue'

export default {
  name: 'App',
  components: {
    TopBar
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

.app-main {
  background: #000000;
}
</style>