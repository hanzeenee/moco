<template>
  <v-app class="app-shell">
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
import axios from 'axios'
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
      }
    }
  },

  async mounted() {
    await this.loadCurrentUser()
  },

  methods: {
    async loadCurrentUser() {
      try {
        const response = await axios.get('/api/accounts/me/')
        if (response.data.authenticated) {
          this.setLoggedInUser(response.data.user)
        }
      } catch (error) {
        this.isLoggedIn = false
        this.userName = ''
      }
    },

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
    },

    handleSignupSuccess(payload) {
      this.isSignupOpen = false
      this.loginForm.username = payload.username
      this.isLoginOpen = true
    },

    setLoggedInUser(user) {
      this.isLoggedIn = true
      this.userName = user.display_name || user.username
    },

    handleLoginSuccess(user) {
      this.setLoggedInUser(user)
      this.closeAllModals()
    },

    async handleLogout() {
      try {
        await axios.post('/api/accounts/logout/')
      } finally {
        this.isLoggedIn = false
        this.userName = ''
        this.closeAllModals()
        this.$router.push('/')
      }
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
