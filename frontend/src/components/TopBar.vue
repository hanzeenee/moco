<template>
  <header class="topbar">
    <!-- 좌측 로고 -->
    <div class="brand" @click="goHome">
      MOCO
    </div>

    <!-- 중앙 메뉴 -->
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

    <!-- 우측 메뉴 -->
    <div class="right-menu">
      <button class="right-btn" @click="goLink('https://www.naver.com')">
        로그인
      </button>

      <button class="right-btn" @click="goLink('https://www.naver.com')">
        회원가입
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: "TopBar",

  data() {
    return {
      buttons: [
        { name: "홈", type: "route", value: "/" },
        { name: "강의", type: "route", value: "/lecture" },
        { name: "유튜브", type: "link", value: "https://www.youtube.com" },
        { name: "카페", type: "link", value: "https://cafe.naver.com" },
        { name: "EA의뢰", type: "link", value: "https://cafe.naver.com" },
        { name: "PT", type: "link", value: "https://cafe.naver.com" },
        { name: "이벤트", type: "route", value: "/event" }
      ]
    };
  },

  methods: {
    goHome() {
      this.$router.push('/');
    },

    goLink(url) {
      window.open(url, "_blank", "noopener,noreferrer");
    },

    handleMenuClick(btn) {
      if (btn.type === 'route') {
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
}

.brand {
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
}

.nav {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 14px;
}

.right-menu {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.nav-btn {
  padding: 8px 14px;
  border: 1px solid #444;
  background: transparent;
  color: #ffffff;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
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
}

.right-btn:hover {
  text-decoration: underline;
}
</style>