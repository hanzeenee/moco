<template>
  <header class="topbar">
    <button class="brand" type="button" aria-label="MOCONIX 홈" @click="goHome">
      <img class="brand-logo" src="@/assets/brand/moconix-wordmark.png" alt="MOCONIX" />
    </button>
    <nav class="nav" aria-label="주 메뉴">
      <button class="nav-btn" type="button" @click="goHome">HOME</button>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'TopBar',
  emits: ['go-home'],
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

.nav-btn {
    padding: 8px 10px;
  }
}
</style>
