<template>
  <header class="topbar">
    <button class="brand" type="button" aria-label="MOCONIX 홈" @click="goHome">
      <img class="brand-logo" src="@/assets/brand/moconix-wordmark.png" alt="MOCONIX" />
    </button>

    <nav class="nav" aria-label="주 메뉴">
      <button class="nav-btn" type="button" @click="goHome">HOME</button>
    </nav>

    <div class="right-menu">
      <template v-if="!isLoggedIn">
        <button class="right-btn" type="button" @click="$emit('open-login')">
          로그인
        </button>

        <button class="right-btn" type="button" @click="$emit('open-signup')">
          회원가입
        </button>
      </template>

      <div v-else class="user-dropdown">
        <button class="nav-btn user-btn" type="button">{{ userName }}</button>

        <div class="dropdown-menu">
          <button class="dropdown-btn" type="button" @click="$emit('logout')">
            로그아웃
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  name: 'TopBar',

  emits: ['open-login', 'open-signup', 'logout', 'go-home'],

  props: {
    isLoggedIn: {
      type: Boolean,
      default: false
    },
    userName: {
      type: String,
      default: ''
    }
  },

  methods: {
    goHome() {
      this.$emit('go-home')
    }
  }
}
</script>

<style scoped>
.topbar {
  min-height: 56px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 20px;
  padding: 8px 20px;
  border-bottom: 1px solid #333;
  background: #000000;
  box-sizing: border-box;
}

.brand {
  position: relative;
  justify-self: start;
  width: 160px;
  max-width: 100%;
  height: 32px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  overflow: hidden;
}

/* Frame the supplied wordmark without changing the original image. */
.brand-logo {
  position: absolute;
  top: 50%;
  left: -9%;
  display: block;
  width: 118%;
  max-width: none;
  height: auto;
  transform: translateY(-50%);
}

.brand:focus-visible {
  outline: 2px solid #ffffff;
  outline-offset: 3px;
}

.nav {
  justify-self: center;
  display: flex;
  justify-content: center;
}

.right-menu {
  justify-self: end;
  display: flex;
  gap: 10px;
  align-items: center;
  min-width: 0;
}

.nav-btn {
  padding: 8px 14px;
  border: 1px solid #444;
  background: transparent;
  color: #ffffff;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  white-space: nowrap;
}

.nav-btn:hover {
  background: #222222;
}

.right-btn {
  padding: 8px 14px;
  border: none;
  background: transparent;
  color: #ffffff;
  cursor: pointer;
  font-weight: 600;
  white-space: nowrap;
}

.right-btn:hover {
  text-decoration: underline;
}

.user-dropdown {
  position: relative;
  display: inline-block;
  max-width: 100%;
}

.user-btn {
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  min-width: 100%;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 8px;
  box-sizing: border-box;
  z-index: 10;
  overflow: hidden;
  display: none;
}

.user-dropdown:hover .dropdown-menu,
.user-dropdown:focus-within .dropdown-menu {
  display: block;
}

.dropdown-btn {
  width: 100%;
  padding: 8px 14px;
  border: none;
  background: transparent;
  color: #ffffff;
  text-align: center;
  border-radius: 0;
  cursor: pointer;
  font-weight: 600;
  white-space: nowrap;
  display: flex;
  justify-content: center;
  align-items: center;
}

.dropdown-btn:hover {
  background: #222222;
}

@media (max-width: 600px) {
  .topbar {
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 8px 12px;
    padding: 8px 12px;
  }

  .nav {
    grid-column: 1 / -1;
    grid-row: 2;
  }

  .right-menu {
    grid-column: 2;
    grid-row: 1;
  }

  .nav-btn {
    padding: 8px 10px;
  }
}
</style>
