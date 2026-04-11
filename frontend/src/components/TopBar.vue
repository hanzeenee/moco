<template>
  <header class="topbar">
    <div class="brand" @click="goHome">
      MOCO
    </div>

    <nav class="nav">
      <button
        v-for="btn in buttons"
        :key="btn.name"
        class="nav-btn"
        @click="handleMenuClick(btn)"
      >
        {{ btn.name }}
      </button>
    </nav>

    <div class="right-menu">
      <template v-if="!isLoggedIn">
        <button class="right-btn" @click="$emit('open-login')">
          로그인
        </button>

        <button class="right-btn" @click="$emit('open-signup')">
          회원가입
        </button>
      </template>

      <template v-else>
        <button class="nav-btn" @click="$router.push('/classroom')">
          내 강의실
        </button>

        <button class="nav-btn" @click="$router.push('/event')">
          이벤트 실적
        </button>

        <div class="user-dropdown">
          <button class="nav-btn user-btn">
            {{ userName }}
          </button>

          <div class="dropdown-menu">
            <button class="dropdown-btn" @click="$emit('logout')">
              로그아웃
            </button>
          </div>
        </div>
      </template>
    </div>
  </header>
</template>

<script>
export default {
  name: "TopBar",

  emits: ["open-login", "open-signup", "logout"],

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

  data() {
    return {
      buttons: [
        { name: "홈", type: "route", value: "/" },
        { name: "강의", type: "route", value: "/lecture" },
        { name: "유튜브", type: "link", value: "https://www.youtube.com" },
        { name: "카페", type: "link", value: "https://cafe.naver.com" },
        { name: "EA의뢰", type: "link", value: "https://cafe.naver.com" },
        { name: "PT", type: "link", value: "https://cafe.naver.com" },
        { name: "이벤트", type: "route", value: "/event" },
        { name: "Admin", type: "link", value: "http://127.0.0.1:8000/admin/" }
      ]
    };
  },

  methods: {
    goHome() {
      this.$router.push("/");
    },

    goLink(url) {
      window.open(url, "_blank", "noopener,noreferrer");
    },

    handleMenuClick(btn) {
      if (btn.type === "route") {
        this.$router.push(btn.value);
      } else {
        this.goLink(btn.value);
      }
    }
  }
};
</script>

<style scoped>
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  position: relative;
  padding: 0 20px;
  border-bottom: 1px solid #333;
  background: #000000;
  box-sizing: border-box;
}

.brand {
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  z-index: 2;
}

.nav {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 14px;
  z-index: 1;
}

.right-menu {
  margin-left: auto;
  margin-right: 20px;
  display: flex;
  gap: 10px;
  z-index: 2;
  align-items: center;
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
}

.user-btn {
  width: 100%;
}

.dropdown-menu {
  position: absolute;
  top: 42px;
  left: 0;
  width: 100%;
  background: #111111;
  border: 1px solid #333333;
  border-radius: 8px;
  box-sizing: border-box;
  z-index: 10;
  overflow: hidden;
  display: none;
}

.user-dropdown:hover .dropdown-menu {
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
</style>