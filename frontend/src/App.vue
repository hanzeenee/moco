<template>
  <v-app>
    <TopBar
      :isLoggedIn="isLoggedIn"
      :userName="userName"
      @open-login="openLoginModal"
      @open-signup="openSignupModal"
      @logout="handleLogout"
    />

    <v-main class="app-main">
      <router-view v-slot="{ Component }">
        <component :is="Component" :isLoggedIn="isLoggedIn" />
      </router-view>
    </v-main>

    <LoginModal
      v-if="isLoginOpen"
      :initialUsername="loginForm.username"
      :initialPassword="loginForm.password"
      @close="closeAllModals"
      @login-success="handleLoginSuccess"
    />

    <SignupModal
      v-if="isSignupOpen"
      @close="closeAllModals"
      @signup-success="handleSignupSuccess"
    />
  </v-app>
</template>

<script>
import TopBar from './components/TopBar.vue'
import LoginModal from './components/LoginModal.vue'
import SignupModal from './components/SignupModal.vue'

export default {
  name: 'App',
  components: {
    TopBar,
    LoginModal,
    SignupModal
  },

  data() {
    return {
      isLoginOpen: false,
      isSignupOpen: false,
      isLoggedIn: false,
      userName: '',
      loginForm: {
        username: '',
        password: '',
      }
    }
  },

  mounted() {
    const savedIsLoggedIn = localStorage.getItem('isLoggedIn')
    const savedUserName = localStorage.getItem('userName')

    if (savedIsLoggedIn === 'true') {
      this.isLoggedIn = true
      this.userName = savedUserName || ''
    }
  },

  methods: {
    openLoginModal() {
      this.isSignupOpen = false
      this.isLoginOpen = true
    },

    openSignupModal() {
      this.isLoginOpen = false
      this.isSignupOpen = true
    },

    closeAllModals() {
      this.isLoginOpen = false
      this.isSignupOpen = false
      this.loginForm.username = ''
      this.loginForm.password = ''
    },

    handleSignupSuccess(payload) {
      this.isSignupOpen = false
      this.loginForm.username = payload.username
      this.loginForm.password = payload.password
      this.isLoginOpen = true
    },

    handleLoginSuccess(user) {
      this.isLoggedIn = true
      this.userName = user.name
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('userName', user.name)
      this.closeAllModals()
    },

    handleLogout() {
      this.isLoggedIn = false
      this.userName = ''
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('userName')
      this.closeAllModals()
      this.$router.push('/')
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

.app-main {
  background: #000000;
}
</style>