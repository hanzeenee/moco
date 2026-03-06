<template>
  <v-app>
    <!-- 상단바 -->
    <TopBar />

    <v-main>
      <HelloWorld />
      <!-- router 사용 중이면 아래로 교체 가능 -->
      <!-- <router-view /> -->
    </v-main>
  </v-app>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import TopBar from './components/TopBar.vue'

export default {
  name: 'App',

  components: {
    HelloWorld,
    TopBar,
  },
}
</script>