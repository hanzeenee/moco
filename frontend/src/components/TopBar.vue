<template>
  <header class="topbar">
    <div class="brand">MOCO</div>

    <nav class="nav">
      <button v-for="btn in buttons"
              :key="btn"
              class="nav-btn"
              @click="goToNaver">
        {{ btn }}
      </button>
    </nav>
  </header>
</template>

<script>
export default {
  name: "TopBar",
  data() {
    return {
      buttons: ["A", "B", "C", "D", "E"]
    };
  },
  methods: {
    goToNaver() {
      window.open("https://www.naver.com", "_blank", "noopener,noreferrer");
      // 현재 탭 이동 원하면 아래 사용
      // window.location.href = "https://www.naver.com";
    }
  }
};
</script>

<style scoped>
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid #eaeaea;
  background: #ffffff;
}

.brand {
  font-weight: 700;
}

.nav {
  display: flex;
  gap: 10px;
}

.nav-btn {
  padding: 8px 14px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.nav-btn:hover {
  background: #f3f3f3;
}
</style>